import pytest
from unittest.mock import patch, MagicMock
from backend.features.architecture_decision.service import ArchitectureDecisionService
from backend.features.architecture_decision.schema import ArchitectureDecisionGenerateAI
from backend.features.documentation_template.fields.model import DocumentationTemplateField

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_template():
    template = MagicMock()
    template.templateID = 1
    return template

@pytest.fixture
def mock_project():
    project = MagicMock()
    project.projectID = 1
    project.name = "Test Project"
    return project

@patch("backend.features.architecture_decision.service.DocumentationTemplateService.get_template")
@patch("backend.features.architecture_decision.service.ProjectAttachmentRepository.list_for_project")
@patch("backend.features.architecture_decision.service.retrieve_dynamic_context")
@patch("backend.features.architecture_decision.service.retrieve_aosa_context")
@patch("backend.features.architecture_decision.service.generate_completion")
def test_generate_suggestion_with_ai_full_flow(
    mock_gen, mock_aosa, mock_dynamic, mock_att_repo, mock_get_template,
    mock_db, mock_template, mock_project
):
    mock_get_template.return_value = mock_template
    mock_db.get.return_value = mock_project
    
    field1 = DocumentationTemplateField(fieldID=101, name="Rationale", isRequired=True)
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [field1]
    
    with patch.object(ArchitectureDecisionService, "_load_attachment_text", return_value="dummy context"):
        mock_att_repo.return_value = [MagicMock()]
        
        mock_dynamic.return_value = ["Context chunk"]
        mock_aosa.return_value = ["AOSA chunk"]
        
        mock_gen.return_value = """
        {
            "title": "AI Decision",
            "statusName": "Proposed",
            "fields": [
                {"fieldID": 101, "value": "Because it is better"}
            ]
        }
        """
        
        payload = ArchitectureDecisionGenerateAI(
            projectID=1,
            templateID=1,
            prompt="Optimize for performance"
        )
        
        result = ArchitectureDecisionService.generate_suggestion_with_ai(mock_db, payload)
        
        assert result.title == "AI Decision"
        assert len(result.fields) > 0
        assert result.fields[0].value == "Because it is better"
        assert result.fields[0].fieldID == 101

@patch("backend.features.architecture_decision.service.DocumentationTemplateService.get_template")
def test_generate_suggestion_template_not_found(mock_get_template, mock_db):
    mock_get_template.return_value = None
    payload = ArchitectureDecisionGenerateAI(projectID=1, templateID=99, prompt="test")
    
    with pytest.raises(Exception) as exc:
        ArchitectureDecisionService.generate_suggestion_with_ai(mock_db, payload)
    assert "404" in str(exc.value)
