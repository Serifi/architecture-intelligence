import os
from typing import Optional, List, Dict

from fastapi import HTTPException, status
from pypdf import PdfReader
from sqlalchemy import select, func
from sqlalchemy.orm import Session
import json
import re

from backend.ai.llm_client import generate_completion, LLMError
from backend.ai.rag_service import retrieve_aosa_context, retrieve_dynamic_context
from backend.features.project.attachment.model import ProjectAttachment

from backend.features.project.model import Project
from backend.features.architecture_decision.status.model import Status
from backend.features.documentation_template.model import DocumentationTemplate
from backend.features.architecture_decision.model import ArchitectureDecision
from backend.features.documentation_template.fields.model import DocumentationTemplateField
from backend.features.project.attachment.repository import ProjectAttachmentRepository

from backend.features.architecture_decision.repository import (
    ArchitectureDecisionRepository,
)
from backend.features.architecture_decision.schema import (
    ArchitectureDecisionCreate,
    ArchitectureDecisionUpdate,
    DecisionFieldValueCreate,
    ArchitectureDecisionGenerateAI,
    DecisionDocumentationRead,
    DecisionDocumentationField,
    ArchitectureDecisionAISuggestion,
    ArchitectureDecisionAISuggestionField, ArchitectureDecisionAlternative, ArchitectureDecisionCompareResponse,
    ArchitectureDecisionCompareRequest, ArchitectureDecisionChatRequest,
)
from backend.features.documentation_template.service import DocumentationTemplateService
from backend.features.architecture_decision.history.service import DecisionHistoryService
from backend.features.project.attachment.service import ATTACHMENTS_DIR


class ArchitectureDecisionService:
    @staticmethod
    def list_by_project(db: Session, project_id: int):
        return ArchitectureDecisionRepository.list_by_project(db, project_id)

    @staticmethod
    def list_all(db: Session):
        return ArchitectureDecisionRepository.list_all(db)

    @staticmethod
    def get(db: Session, decision_id: int):
        decision = ArchitectureDecisionRepository.get_by_id(db, decision_id)
        if decision is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Architecture decision not found.",
            )
        return decision

    @staticmethod
    def _title_exists(db: Session, title: str, exclude_id: Optional[int] = None) -> bool:
        stmt = select(func.count(ArchitectureDecision.decisionID)).where(
            ArchitectureDecision.title == title
        )
        if exclude_id is not None:
            stmt = stmt.where(ArchitectureDecision.decisionID != exclude_id)
        return (db.execute(stmt).scalar() or 0) > 0

    @staticmethod
    def _validate_foreign_keys(db: Session, project_id: int, template_id: int, status_id: Optional[int], field_values: Optional[List[DecisionFieldValueCreate]], title: str, action: str, enforce_required: bool = True):
        project = db.get(Project, project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Architecture decision '{title}' cannot be {action}: project not found.",
            )

        template = db.get(DocumentationTemplate, template_id)
        if template is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Architecture decision '{title}' cannot be {action}: template not found.",
            )

        if status_id is not None:
            status_obj = db.get(Status, status_id)
            if status_obj is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Architecture decision '{title}' cannot be {action}: status not found.",
                )

        template_field_ids = {f.fieldID for f in template.fields}
        required_field_ids = {f.fieldID for f in template.fields if f.isRequired}

        provided = field_values or []
        provided_ids = {fv.fieldID for fv in provided}

        for fv in provided:
            if fv.fieldID not in template_field_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Architecture decision '{title}' cannot be {action}: "
                        f"field {fv.fieldID} does not belong to template {template_id}."
                    ),
                )

        if enforce_required:
            missing_required = required_field_ids - provided_ids
            if missing_required:
                missing_list = ", ".join(str(x) for x in sorted(missing_required))
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Architecture decision '{title}' cannot be {action}: "
                        f"required fields missing ({missing_list})."
                    ),
                )

            empty_required = [
                fv.fieldID
                for fv in provided
                if fv.fieldID in required_field_ids
                and (fv.value is None or str(fv.value).strip() == "")
            ]
            if empty_required:
                empty_list = ", ".join(str(x) for x in sorted(empty_required))
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Architecture decision '{title}' cannot be {action}: "
                        f"required fields empty ({empty_list})."
                    ),
                )

    @staticmethod
    def create(db: Session, payload: ArchitectureDecisionCreate):
        if payload.title is None or not payload.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Architecture decision cannot be created: title is required.",
            )

        if ArchitectureDecisionService._title_exists(db, payload.title):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Architecture decision '{payload.title}' cannot be created: title already exists.",
            )

        ArchitectureDecisionService._validate_foreign_keys(
            db=db,
            project_id=payload.projectID,
            template_id=payload.templateID,
            status_id=payload.statusID,
            field_values=payload.fieldValues,
            title=payload.title,
            action="created",
            enforce_required=True,
        )

        decision = ArchitectureDecisionRepository.create(
            db,
            project_id=payload.projectID,
            template_id=payload.templateID,
            status_id=payload.statusID,
            title=payload.title,
            field_values=payload.fieldValues,
        )

        DecisionHistoryService.add_created_entry(db, decision.decisionID, payload.userID)

        return {
            "message": f"Architecture decision '{decision.title}' was created successfully.",
            "decision": decision,
        }

    @staticmethod
    def update(db: Session, decision_id: int, payload: ArchitectureDecisionUpdate):
        decision_before = ArchitectureDecisionService.get(db, decision_id)

        if payload.title is not None and ArchitectureDecisionService._title_exists(
            db, payload.title, exclude_id=decision_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Architecture decision '{payload.title}' cannot be updated: title already exists.",
            )

        template_changed = (
            payload.templateID is not None
            and payload.templateID != decision_before.templateID
        )
        field_values_provided = payload.fieldValues is not None

        effective_project_id = decision_before.projectID
        effective_template_id = payload.templateID or decision_before.templateID
        effective_status_id = (
            payload.statusID if payload.statusID is not None else decision_before.statusID
        )
        effective_title = payload.title or decision_before.title

        enforce_required = template_changed or field_values_provided

        if field_values_provided and not template_changed:
            existing_map: Dict[int, Optional[str]] = {
                fv.fieldID: fv.value for fv in decision_before.fieldValues
            }
            for fv in payload.fieldValues:
                existing_map[fv.fieldID] = fv.value

            effective_field_values: List[DecisionFieldValueCreate] = [
                DecisionFieldValueCreate(fieldID=fid, value=val)
                for fid, val in existing_map.items()
            ]
        else:
            effective_field_values = (
                payload.fieldValues
                if field_values_provided
                else decision_before.fieldValues
            )

        ArchitectureDecisionService._validate_foreign_keys(
            db=db,
            project_id=effective_project_id,
            template_id=effective_template_id,
            status_id=effective_status_id,
            field_values=effective_field_values,
            title=effective_title,
            action="updated",
            enforce_required=enforce_required,
        )

        previous_status_id = decision_before.statusID
        previous_field_values_map: Dict[int, Optional[str]] = {
            fv.fieldID: fv.value for fv in decision_before.fieldValues
        }

        updated = ArchitectureDecisionRepository.update(
            db,
            decision=decision_before,
            template_id=payload.templateID,
            status_id=payload.statusID,
            title=payload.title,
            field_values=payload.fieldValues,
        )

        if payload.statusID is not None and payload.statusID != previous_status_id:
            DecisionHistoryService.add_status_change_entry(
                db, decision_id, payload.userID
            )

        changed_fields: Dict[int, Optional[str]] = {}
        if payload.fieldValues is not None:
            for fv in payload.fieldValues:
                old_val = previous_field_values_map.get(fv.fieldID)
                new_val = fv.value
                if (old_val or "") != (new_val or ""):
                    changed_fields[fv.fieldID] = new_val

        if changed_fields:
            DecisionHistoryService.add_field_change_entries(
                db, decision_id, changed_fields, payload.userID
            )

        return {
            "message": f"Architecture decision '{updated.title}' was updated successfully.",
            "decision": updated,
        }

    @staticmethod
    def delete(db: Session, decision_id: int):
        decision = ArchitectureDecisionService.get(db, decision_id)
        title = decision.title
        ArchitectureDecisionRepository.delete(db, decision)
        return {"message": f"Architecture decision '{title}' was deleted successfully."}

    @staticmethod
    def get_documentation(db: Session, decision_id: int) -> DecisionDocumentationRead:
        decision = ArchitectureDecisionRepository.get_with_template_and_values(
            db, decision_id
        )
        if decision is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Architecture decision not found.",
            )

        fields: List[DecisionDocumentationField] = []
        values_by_field = {fv.fieldID: fv.value for fv in decision.fieldValues}

        for f in decision.template.fields:
            fields.append(
                DecisionDocumentationField(
                    fieldID=f.fieldID,
                    name=f.name,
                    isRequired=f.isRequired,
                    value=values_by_field.get(f.fieldID),
                )
            )

        return DecisionDocumentationRead(
            decisionID=decision.decisionID,
            projectID=decision.projectID,
            statusID=decision.statusID,
            title=decision.title,
            templateID=decision.templateID,
            templateName=decision.template.name,
            fields=fields,
        )

    @staticmethod
    def _load_attachment_text(attachment: ProjectAttachment, project_id: int) -> Optional[str]:
        path = os.path.join(ATTACHMENTS_DIR, str(project_id), attachment.storedFilename)
        if not os.path.exists(path):
            return None

        filename_lower = (attachment.originalFilename or "").lower()
        mime = (attachment.mimeType or "").lower()

        if mime == "application/pdf" or filename_lower.endswith(".pdf"):
            try:
                reader = PdfReader(path)
                texts: List[str] = []
                for page in reader.pages:
                    t = page.extract_text() or ""
                    t = t.strip()
                    if t:
                        texts.append(t)
                return "\n".join(texts) if texts else None
            except Exception:
                return None

        if mime.startswith("text/") or filename_lower.endswith((".txt", ".md", ".rst")):
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                return content or None
            except Exception:
                return None


        return None

    @staticmethod
    def _chunk_text(text: str, max_chars: int = 800) -> List[str]:

        chunks: List[str] = []
        buffer = ""

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if len(buffer) + len(line) + 1 > max_chars:
                if buffer:
                    chunks.append(buffer)
                buffer = line
            else:
                buffer = (buffer + " " + line).strip()

        if buffer:
            chunks.append(buffer)

        return chunks


    @staticmethod
    def generate_suggestion_with_ai(db: Session, payload: ArchitectureDecisionGenerateAI) -> ArchitectureDecisionAISuggestion:
        template = DocumentationTemplateService.get_template(db, payload.templateID)
        if template is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="DocumentationTemplate not found",
            )

        fields = (
            db.query(DocumentationTemplateField)
            .filter(DocumentationTemplateField.templateID == payload.templateID)
            .order_by(DocumentationTemplateField.fieldID)
            .all()
        )
        if not fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template has no fields",
            )

        project = db.get(Project, payload.projectID)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        attachments = ProjectAttachmentRepository.list_for_project(db, payload.projectID)

        all_chunks: List[str] = []
        for att in attachments:
            content = ArchitectureDecisionService._load_attachment_text(
                att, payload.projectID
            )
            if not content:
                continue
            all_chunks.extend(
                ArchitectureDecisionService._chunk_text(content, max_chars=800)
            )

        if not all_chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No suitable project documentation found for scenario context. "
                    "Add at least one readable attachment (e.g. PDF or text file)."
                ),
            )

        scenario_label = getattr(project, "name", None) or f"project {project.projectID}"

        decision_summary = (
            f"We want to make an architecture decision for {scenario_label} "
            f"with primary quality attribute '{payload.prompt}'."
        )

        scenario_query = (
            f"{scenario_label}: architecture, domain concepts, components and constraints. "
            f"Focus on quality attribute {payload.prompt}."
        )
        scenario_chunks = retrieve_dynamic_context(
            query=scenario_query,
            texts=all_chunks,
            k=4,
        )
        scenario_context = "\n\n---\n\n".join(scenario_chunks)

        aosa_query = (
            f"Architecture patterns and trade-offs for a system like {scenario_label} "
            f"with focus on {payload.prompt}."
        )
        aosa_chunks = retrieve_aosa_context(aosa_query, k=4)
        aosa_context = "\n\n---\n\n".join(aosa_chunks)

        field_skeleton = ",\n".join([f'  {{"fieldID": {f.fieldID}, "value": ""}}' for f in fields])


        prompt = f"""
                    You are generating an Architecture Decision for a specific software system.
                    
                    IMPORTANT CONTEXT LOCK:
                    - The ONLY authoritative sources for this decision are: 
                      (1) the "System scenario (from project documentation files)" and
                      (2) the provided decision prompt describing the quality attribute and decision intent.
                    - Both sources are EQUALLY critical and MUST be reflected in every alternative.
                    - Do NOT rely on general knowledge unless it clearly aligns with the scenario.
                    - If something is not stated or inferable from the scenario, treat it as missing information.

                    System scenario (from project documentation files):
                    {scenario_context}
                    
                    Decision prompt describing the quality attribute and decision intent:
                    {payload.prompt}
                    
                    General architectural knowledge (for reasoning support only, not as facts):
                    {aosa_context}
                    
                    Template fields (IDs and names):
                    {chr(10).join([f"- {f.fieldID}: {f.name}" for f in fields])}
                
                    Decision goal:
                    {decision_summary}
                
                    DECISION TASK:
                    - Document an architecture decision for THIS system using the given template.
                    - Every field MUST reflect the system scenario explicitly.
                    
                    FIELD EVIDENCE RULE (CRITICAL):
                    - For EACH template field, derive the value from:
                      (a) explicit statements in the scenario, or
                      (b) a clearly stated assumption that is consistent with the scenario.
                    - Do NOT invent components, technologies, or constraints not implied by the scenario.
                    
                    ASSUMPTION RULE:
                    - If you must assume something, clearly phrase it as an assumption.
                    - Assumptions must be minimal and realistic for the given system.
                    
                    OUTPUT RULES:
                    - Return ONLY one valid JSON object.
                    - ALL template fieldIDs must be present.
                    - No empty values.
                    
                    Allowed statusName:
                    "Proposed"
                    
                    Now produce JSON using this EXACT skeleton (fill in values, keep all items):
                    {{
                      "title": "...",
                      "statusName": "Proposed",
                      "fields": [
                        {field_skeleton}
                      ]
                    }}
                """

        try:
            raw = generate_completion(prompt)
        except LLMError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"LLM error: {e}",
            )

        def _extract_json(raw_text: str) -> dict:
            try:
                return json.loads(raw_text)
            except json.JSONDecodeError:
                pass

            fenced = re.search(r"```json(.*)```", raw_text, re.DOTALL | re.IGNORECASE)
            if fenced:
                inner = fenced.group(1).strip()
                try:
                    return json.loads(inner)
                except json.JSONDecodeError:
                    pass

            first = raw_text.find("{")
            last = raw_text.rfind("}")
            if first != -1 and last != -1 and first < last:
                candidate = raw_text[first : last + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    pass

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="LLM returned invalid JSON",
            )

        data = _extract_json(raw)

        title = data.get("title") or "AI-generated architecture decision"
        status_name = data.get("statusName") or "Proposed"

        values_by_id: Dict[int, str] = {}
        for fv in data.get("fields", []):
            try:
                field_id = int(fv["fieldID"])
                value = str(fv.get("value", "")).strip()
            except (KeyError, ValueError, TypeError):
                continue
            if value:
                values_by_id[field_id] = value

        suggestion_fields: List[ArchitectureDecisionAISuggestionField] = []
        missing_required: List[int] = []

        for f in fields:
            val = values_by_id.get(f.fieldID)
            if f.isRequired and not val:
                missing_required.append(f.fieldID)
            suggestion_fields.append(
                ArchitectureDecisionAISuggestionField(
                    fieldID=f.fieldID,
                    name=f.name,
                    isRequired=f.isRequired,
                    value=val,
                )
            )

        if missing_required:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                        "LLM did not fill all required fields: "
                        + ", ".join(str(fid) for fid in missing_required)
                ),
            )

        return ArchitectureDecisionAISuggestion(
            title=title,
            statusName=status_name,
            fields=suggestion_fields,
        )

    @staticmethod
    def _load_project_chunks(db: Session, project_id: int) -> tuple[str, List[str]]:
        project = db.get(Project, project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        attachments = ProjectAttachmentRepository.list_for_project(db, project_id)

        all_chunks: List[str] = []
        for att in attachments:
            content = ArchitectureDecisionService._load_attachment_text(att, project_id)
            if not content:
                continue
            all_chunks.extend(
                ArchitectureDecisionService._chunk_text(content, max_chars=800)
            )

        if not all_chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No suitable project documentation found for scenario context. "
                    "Add at least one readable attachment (e.g. PDF or text file)."
                ),
            )

        scenario_label = project.name or "this project"
        return scenario_label, all_chunks

    @staticmethod
    def generate_alternatives_with_ai(db: Session, payload: ArchitectureDecisionCompareRequest) -> ArchitectureDecisionCompareResponse:
        template = DocumentationTemplateService.get_template(db, payload.templateID)
        if template is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="DocumentationTemplate not found",
            )

        fields = (
            db.query(DocumentationTemplateField)
            .filter(DocumentationTemplateField.templateID == payload.templateID)
            .order_by(DocumentationTemplateField.fieldID)
            .all()
        )
        if not fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template has no fields",
            )

        scenario_label, all_chunks = ArchitectureDecisionService._load_project_chunks(
            db, payload.projectID
        )

        scenario_query = (
            f"{scenario_label}: architecture, domain concepts, components and constraints. "
            f"Focus on quality attribute {payload.prompt}."
        )
        scenario_chunks = retrieve_dynamic_context(
            query=scenario_query,
            texts=all_chunks,
            k=4,
        )
        scenario_context = "\n\n---\n\n".join(scenario_chunks)

        aosa_query = (
            f"Architecture patterns and trade-offs for {scenario_label} "
            f"with focus on {payload.prompt}."
        )
        aosa_chunks = retrieve_aosa_context(aosa_query, k=4)
        aosa_context = "\n\n---\n\n".join(aosa_chunks)

        field_desc = "\n".join(f"- {f.fieldID}: {f.name}" for f in fields)

        base = payload.base
        base_fields_desc = "\n".join(
            f"- {f.fieldID} ({f.name}): {f.value or ''}"
            for f in base.fields
        )

        field_skeleton_alt = ",\n".join(
            [f'        {{"fieldID": {f.fieldID}, "value": ""}}' for f in fields]
        )

        prompt = f"""
                    You are comparing architecture decision alternatives for a specific software system.
            
                    IMPORTANT CONTEXT LOCK:
                    - The ONLY authoritative sources for the alternatives are:
                      (1) the "System scenario (from project documentation files)" and
                      (2) the provided decision prompt describing the quality attribute and decision intent.
                    - Both sources are EQUALLY critical and MUST be reflected in every alternative.
                    - Do NOT rely on general knowledge unless it clearly aligns with the scenario.
                    - If something is not stated or inferable from the scenario, treat it as missing information.
                    
                    System scenario (from project documentation files):
                    {scenario_context}
            
                    General architectural knowledge (for reasoning support only, not as facts):
                    {aosa_context}
            
                    Template fields (IDs and names):
                    {field_desc}
            
                    Decision prompt describing the quality attribute and decision intent:
                    {payload.prompt}
            
                    Current decision (base):
                    - Title: {base.title}
                    - Status: {base.statusName or "Proposed"}
                    - Fields:
                    {base_fields_desc}
            
                    TASK:
                    - Propose exactly {payload.numberOfAlternatives} alternative architecture decisions for THIS same system.
                    - Each alternative MUST be a plausible option given the scenario context and the template.
                    - Each alternative MUST differ meaningfully from the base (different trade-offs, not just rewording).
                    - Then provide a concise comparisonSummary.

                    DECISION DOCUMENTATION REQUIREMENT:
                    - You MUST document each alternative using the given template fields.
                    - Every field value MUST reflect the system scenario explicitly.

                    FIELD EVIDENCE RULE (CRITICAL):
                    - For EACH template field, derive the value from:
                      (a) explicit statements in the scenario, or
                      (b) a clearly stated assumption that is consistent with the scenario.
                    - Do NOT invent components, technologies, stakeholders, constraints, or requirements not implied by the scenario.

                    ASSUMPTION RULE:
                    - If you must assume something, clearly phrase it as an assumption.
                    - Assumptions must be minimal and realistic for the given system.
                    - Keep assumptions consistent across fields within one alternative.

                    OUTPUT RULES (MUST FOLLOW):
                    1) Return ONLY one valid JSON object. No Markdown, no comments.
                    2) The JSON MUST contain exactly these keys: "alternatives", "comparisonSummary".
                    3) "alternatives" MUST contain exactly {payload.numberOfAlternatives} items.
                    4) For EACH alternative:
                       - It MUST contain exactly these keys: "title", "statusName", "fields".
                       - "fields" MUST contain EVERY template fieldID exactly once (no missing, no duplicates).
                       - EVERY field MUST have a non-empty "value".
                    5) Before returning the JSON, do a self-check and fix issues:
                       - Are all fieldIDs present exactly once in every alternative? If not, fix it.
                       - Are any values empty? If yes, fill them with a minimal assumption.
            
                    Allowed statusName:
                    "Proposed"
            
                    Important: Top-level "title" and "statusName" do NOT replace any template fields.
                    If the template contains fields named "Title" or "Status", you MUST still fill them in "fields".
            
                    Now produce JSON using this EXACT skeleton (fill in values, keep all items):
                    {{
                      "alternatives": [
                        {{
                          "title": "...",
                          "statusName": "Proposed",
                          "fields": [
                    {field_skeleton_alt}
                          ]
                        }}
                      ],
                      "comparisonSummary": "..."
                    }}
                """

        try:
            raw = generate_completion(prompt)
        except LLMError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"LLM error: {e}",
            )

        def _extract_json(raw_text: str) -> dict:
            try:
                return json.loads(raw_text)
            except json.JSONDecodeError:
                pass

            fenced = re.search(r"```json(.*)```", raw_text, re.DOTALL | re.IGNORECASE)
            if fenced:
                inner = fenced.group(1).strip()
                try:
                    return json.loads(inner)
                except json.JSONDecodeError:
                    pass

            first = raw_text.find("{")
            last = raw_text.rfind("}")
            if first != -1 and last != -1 and first < last:
                candidate = raw_text[first : last + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    pass

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="LLM returned invalid JSON",
            )

        data = _extract_json(raw)

        raw_alts = data.get("alternatives") or []
        comparison_summary = data.get("comparisonSummary") or ""

        alternatives: List[ArchitectureDecisionAlternative] = []
        for alt in raw_alts:
            title = alt.get("title") or "AI-generated alternative"
            status_name = alt.get("statusName") or "Proposed"

            values_by_id: Dict[int, str] = {}
            for fv in alt.get("fields", []):
                try:
                    field_id = int(fv["fieldID"])
                    value = str(fv.get("value", "")).strip()
                except (KeyError, ValueError, TypeError):
                    continue
                if value:
                    values_by_id[field_id] = value

            suggestion_fields: List[ArchitectureDecisionAISuggestionField] = []
            missing_required: List[int] = []

            for f in fields:
                val = values_by_id.get(f.fieldID)
                if f.isRequired and not val:
                    missing_required.append(f.fieldID)
                suggestion_fields.append(
                    ArchitectureDecisionAISuggestionField(
                        fieldID=f.fieldID,
                        name=f.name,
                        isRequired=f.isRequired,
                        value=val,
                    )
                )

            if missing_required:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=(
                            "LLM did not fill all required fields for an alternative: "
                            + ", ".join(str(fid) for fid in missing_required)
                    ),
                )

            alternatives.append(
                ArchitectureDecisionAlternative(
                    title=title,
                    statusName=status_name,
                    fields=suggestion_fields,
                )
            )

        return ArchitectureDecisionCompareResponse(
            base=payload.base,
            alternatives=alternatives,
            comparisonSummary=comparison_summary,
        )

    @staticmethod
    def chat_about_decision(db: Session, payload: ArchitectureDecisionChatRequest) -> str:
        scenario_label, all_chunks = ArchitectureDecisionService._load_project_chunks(
            db, payload.projectID
        )

        scenario_query = (
            f"{scenario_label}: architecture, domain concepts, components and constraints."
        )
        scenario_chunks = retrieve_dynamic_context(
            query=scenario_query,
            texts=all_chunks,
            k=4,
        )
        scenario_context = "\n\n---\n\n".join(scenario_chunks)

        aosa_query = (
            f"Architecture patterns and trade-offs relevant for {scenario_label}. "
            f"Focus on qualities mentioned in the conversation and suggestion."
        )
        aosa_chunks = retrieve_aosa_context(aosa_query, k=4)
        aosa_context = "\n\n---\n\n".join(aosa_chunks)

        if payload.suggestion is not None:
            sug = payload.suggestion
            sug_fields_lines: List[str] = []
            for f in sug.fields:
                sug_fields_lines.append(
                    f"- {f.fieldID} ({f.name}, required={f.isRequired}): {f.value or ''}"
                )
            suggestion_block = (
                f"Title: {sug.title}\n"
                f"Status: {sug.statusName or 'Proposed'}\n"
                f"Fields:\n" + "\n".join(sug_fields_lines)
            )
        else:
            suggestion_block = "No explicit AI-generated suggestion provided."

        convo_lines: List[str] = []
        for m in payload.messages:
            convo_lines.append(f"{m.role.upper()}: {m.content}")
        conversation = "\n".join(convo_lines)

        last_user_msg = ""
        for m in reversed(payload.messages):
            if m.role == "user":
                last_user_msg = m.content
                break

        prompt = f"""
                    You are an assistant helping to refine and discuss architecture decisions for a software system.
                    
                    System scenario (from project documentation files):
                    {scenario_context}
                    
                    General architectural knowledge (from 'The Architecture Of Open Source Applications'):
                    {aosa_context}
                    
                    Current AI-generated suggestion:
                    {suggestion_block}
                    
                    Conversation so far:
                    {conversation}
                    
                    User's latest message:
                    {last_user_msg}
                    
                    Instructions:
                    - Answer as an experienced software architect.
                    - Base your reasoning primarily on the project scenario, the current suggestion, and the AOSA context.
                    - Explain trade-offs and possible decision options when helpful.
                    - Do NOT output Markdown or JSON structure explanations.
                    - Return ONLY a JSON object of the form:
                      {{"reply": "natural language answer to the user"}}
                """

        try:
            raw = generate_completion(prompt)
        except LLMError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"LLM error: {e}",
            )

        def _extract_json(raw_text: str) -> dict:
            try:
                return json.loads(raw_text)
            except json.JSONDecodeError:
                pass

            fenced = re.search(r"```json(.*)```", raw_text, re.IGNORECASE | re.DOTALL)
            if fenced:
                inner = fenced.group(1).strip()
                try:
                    return json.loads(inner)
                except json.JSONDecodeError:
                    pass

            first = raw_text.find("{")
            last = raw_text.rfind("}")
            if first != -1 and last != -1 and first < last:
                candidate = raw_text[first:last + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    pass

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="LLM returned invalid JSON",
            )

        data = _extract_json(raw)
        reply = data.get("reply")
        if not reply:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="LLM did not return 'reply' field.",
            )
        return reply