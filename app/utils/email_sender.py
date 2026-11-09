from app.config import settings

def send_email(recipient: str, subject: str, body: str) -> None:
    """Faux expÃ©diteur local : aucun email rÃ©el n'est envoyÃ©."""
    if settings.fail_notifications:
        raise RuntimeError("Simulation : le service de notification est indisponible")
    print(f"[FAKE EMAIL] to={recipient} subject={subject} body={body}")
