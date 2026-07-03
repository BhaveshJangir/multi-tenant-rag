import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import ChatRequest, ChatSession as ChatSessionSchema
from app.core.agent import app_graph
from langchain_core.messages import HumanMessage

router = APIRouter()

@router.post("/", response_model=dict)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Chat with the knowledge base using the LangGraph agent workflow.
    """
    session_id = request.session_id
    
    # 1. Handle Session
    if not session_id:
        session_id = str(uuid.uuid4())
        new_session = ChatSession(
            id=session_id,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            title=request.query[:50]
        )
        db.add(new_session)
        await db.commit()
    else:
        # Verify session exists and belongs to tenant
        result = await db.execute(select(ChatSession).filter(ChatSession.id == session_id))
        session = result.scalars().first()
        if not session or session.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=404, detail="Session not found")
            
    # 2. Save User Message
    user_msg = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="user",
        content=request.query
    )
    db.add(user_msg)
    
    # 3. Fetch past messages for context (Memory)
    result = await db.execute(
        select(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp.asc())
    )
    past_messages = result.scalars().all()
    
    # 4. Convert to LangChain format
    langchain_messages = []
    for msg in past_messages:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        # Add AIMessage logic here if needed
        
    langchain_messages.append(HumanMessage(content=request.query))
    
    # 5. Invoke LangGraph Workflow
    try:
        final_state = app_graph.invoke({
            "messages": langchain_messages,
            "tenant_id": current_user.tenant_id
        })
        ai_response_content = final_state["messages"][-1].content
    except Exception as e:
        ai_response_content = f"Error generating response: {str(e)}"
        
    # 6. Save AI Message
    ai_msg = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="assistant",
        content=ai_response_content
    )
    db.add(ai_msg)
    await db.commit()
    
    return {
        "session_id": session_id,
        "response": ai_response_content
    }
