from fastapi import APIRouter, Request, Depends, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db, SpottedMessage, MessageStatus
from app.tasks import moderate_message_task
from config import settings

router = APIRouter(
    prefix="/spotted",
    tags=["Web Interface"]
)

templates = Jinja2Templates(directory="app/web/templates")

@router.get("/new", response_class=HTMLResponse)
def show_submission_form(request: Request, success: bool = False, error: str = None):
    return templates.TemplateResponse("index.html", {"request": request, "success": success, "error": error})

@router.post("/submit")
def handle_submission(
    request: Request,
    background_tasks: BackgroundTasks,
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Gestisce l'invio del form, salva il messaggio con stato PENDING
    e avvia un task in background per la moderazione AI.
    """
    print("--- NUOVA LOGICA DI INVIO UTILIZZATA ---") # Messaggio di log chiaro

    if not message or len(message.strip()) < 10:
        return RedirectResponse(url=str(request.url_for('show_submission_form')) + "?error=Il+messaggio+deve+contenere+almeno+10+caratteri.", status_code=303)

    new_message = SpottedMessage(
        text=message.strip(),
        status=MessageStatus.PENDING
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    print(f"Nuovo messaggio (ID: {new_message.id}) salvato. Avvio moderazione AI in background...")

    background_tasks.add_task(moderate_message_task, new_message.id)

    return RedirectResponse(url=str(request.url_for('show_submission_form')) + "?success=true", status_code=303)