from src.app import activities


def test_root_redirects_to_static_page(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_catalog(client):
    # Arrange
    expected_activity_count = len(activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == expected_activity_count
    assert response.json()["Chess Club"]["participants"] == activities["Chess Club"]["participants"]


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_duplicate_signup_is_rejected_case_insensitively(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]
    participant_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": existing_email.upper()},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert len(activities[activity_name]["participants"]) == participant_count


def test_signup_for_unknown_activity_returns_not_found(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant_case_insensitively(client):
    # Arrange
    activity_name = "Chess Club"
    participant = activities[activity_name]["participants"][0]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{participant.upper()}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {participant} from {activity_name}"
    assert participant not in activities[activity_name]["participants"]


def test_unregister_absent_participant_returns_not_found(client):
    # Arrange
    activity_name = "Chess Club"
    email = "absent@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_from_unknown_activity_returns_not_found(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/student@mergington.edu"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
