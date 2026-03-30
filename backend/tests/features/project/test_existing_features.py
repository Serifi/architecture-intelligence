import pytest
from backend.features.project.service import ProjectService
from backend.features.project.schema import ProjectCreate, ProjectUpdate
from backend.features.project.enum import PriorityLevel

def test_project_position_negative_value(db_session, sample_user):
    from pydantic import ValidationError
    
    with pytest.raises(ValidationError):
        payload = ProjectCreate(
            name="Negative Position",
            description="Test",
            priority=PriorityLevel.LOW,
            position=-1,  
            icon="folder",
            color="#000000"
        )


def test_project_update_lastUpdated_timestamp(db_session, sample_project, sample_user):
    import time
    original_time = sample_project.lastUpdated
    
    time.sleep(1)
    
    payload = ProjectUpdate(name="Updated Name")
    result = ProjectService.update_project(
        db_session, 
        sample_project.projectID, 
        payload, 
        sample_user.userID
    )
    
    assert result["project"].lastUpdated > original_time, \
        "lastUpdated should be updated when content changes"


def test_project_tags_empty_string_filtered(db_session, sample_user):
    from pydantic import ValidationError
    
    with pytest.raises(ValidationError):
        payload = ProjectCreate(
            name="Empty Tags Test",
            description="Test",
            priority=PriorityLevel.LOW,
            position=0,
            icon="folder",
            color="#000000",
            tags=["", "  ", "valid"]  
        )


def test_project_color_invalid_hex(db_session, sample_user):
    from pydantic import ValidationError
    
    with pytest.raises(ValidationError):
        payload = ProjectCreate(
            name="Invalid Color",
            description="Test",
            priority=PriorityLevel.LOW,
            position=0,
            icon="folder",
            color="#GGGGGG"  
        )


def test_project_reorder_preserves_data(db_session, sample_user):
    from backend.features.project.schema import ProjectReorderPayload, ProjectReorderItem
    
    p1 = ProjectService.create_project(db_session, ProjectCreate(
        name="Project A",
        description="Description A",
        priority=PriorityLevel.HIGH,
        position=0,
        icon="star",
        color="#FF0000",
        tags=["tag1", "tag2"]
    ), sample_user.userID)
    
    p2 = ProjectService.create_project(db_session, ProjectCreate(
        name="Project B",
        description="Description B",
        priority=PriorityLevel.LOW,
        position=1,
        icon="folder",
        color="#00FF00",
        tags=["tag3"]
    ), sample_user.userID)
    
    payload = ProjectReorderPayload(items=[
        ProjectReorderItem(projectID=p2["project"].projectID, position=0),
        ProjectReorderItem(projectID=p1["project"].projectID, position=1)
    ])
    
    ProjectService.reorder_projects(db_session, payload, sample_user.userID)

    db_session.refresh(p1["project"])
    db_session.refresh(p2["project"])
    
    assert p1["project"].name == "Project A", "Name should not change after reorder"
    assert p1["project"].description == "Description A", "Description should not change"
    assert p1["project"].tags == ["tag1", "tag2"], "Tags should not change"
    assert p1["project"].color == "#FF0000", "Color should not change"
