import pytest

from core.models import Lead


@pytest.mark.django_db
class TestB2BForm:
    def test_b2b_page_has_form_action(self, client):
        response = client.get("/b2b/")
        assert response.status_code == 200
        assert b'action="/b2b/trial-request/"' in response.content

    def test_b2b_page_renders_form_fields(self, client):
        content = client.get("/b2b/").content
        for name in (b"contact_name", b"company", b"phone", b"email", b"message"):
            assert f'name="{name.decode()}"'.encode() in content

    def test_trial_request_valid_creates_lead(self, client):
        response = client.post("/b2b/trial-request/", {
            "contact_name": "Иван Иванов",
            "company": "Ресторан «Вкус»",
            "phone": "+375291111111",
            "email": "ivan@rest.by",
            "message": "Хочу пробную партию",
        })
        assert response.status_code == 302
        assert Lead.objects.count() == 1
        lead = Lead.objects.get()
        assert lead.source == "b2b"
        assert lead.company == "Ресторан «Вкус»"
        follow = client.get(response["Location"])
        assert "Ваш запрос отправлен".encode() in follow.content

    def test_trial_request_post_to_b2b_url(self, client):
        response = client.post("/b2b/", {
            "contact_name": "Пётр Петров",
            "company": "Кафе «Свежесть»",
            "phone": "+375292222222",
            "email": "petr@cafe.by",
        })
        assert response.status_code == 302
        assert Lead.objects.get().source == "b2b"

    def test_trial_request_invalid_email(self, client):
        response = client.post("/b2b/trial-request/", {
            "contact_name": "Иван Иванов",
            "company": "Ресторан",
            "phone": "+375291111111",
            "email": "not-an-email",
        })
        assert response.status_code == 200
        assert Lead.objects.count() == 0
        assert response.context["form"].errors.get("email")
        assert b"not-an-email" in response.content

    def test_trial_request_missing_required_field(self, client):
        response = client.post("/b2b/trial-request/", {
            "contact_name": "Иван Иванов",
            "company": "Ресторан",
            "phone": "",
            "email": "ivan@rest.by",
        })
        assert response.status_code == 200
        assert Lead.objects.count() == 0
        assert response.context["form"].errors.get("phone")


@pytest.mark.django_db
class TestContactsForm:
    def test_contacts_valid_creates_lead(self, client):
        response = client.post("/contacts/", {
            "contact_name": "Мария Сидорова",
            "email": "maria@mail.by",
            "phone": "+375293333333",
            "message": "Есть вопрос по ассортименту",
        })
        assert response.status_code == 302
        assert Lead.objects.count() == 1
        lead = Lead.objects.get()
        assert lead.source == "contacts"
        assert lead.message == "Есть вопрос по ассортименту"
        follow = client.get(response["Location"])
        assert "Сообщение отправлено".encode() in follow.content

    def test_contacts_phone_optional(self, client):
        response = client.post("/contacts/", {
            "contact_name": "Мария Сидорова",
            "email": "maria@mail.by",
            "message": "Здравствуйте",
        })
        assert response.status_code == 302
        assert Lead.objects.get().phone == ""

    def test_contacts_missing_message(self, client):
        response = client.post("/contacts/", {
            "contact_name": "Мария Сидорова",
            "email": "maria@mail.by",
            "message": "",
        })
        assert response.status_code == 200
        assert Lead.objects.count() == 0
        assert response.context["form"].errors.get("message")

    def test_contacts_invalid_email(self, client):
        response = client.post("/contacts/", {
            "contact_name": "Мария Сидорова",
            "email": "oops",
            "message": "Текст",
        })
        assert response.status_code == 200
        assert Lead.objects.count() == 0
        assert response.context["form"].errors.get("email")
