"""
LangChain을 활용한 AI 챗봇 서비스
OpenAI GPT와 Google Gemini를 지원합니다.
"""
import os
import json
from typing import List, Dict, Optional, Literal, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader

# .env 파일 로드
load_dotenv()

@dataclass
class Message:
    """채팅 메시지 데이터 클래스"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        """타임스탬프 자동 설정"""
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class ChatService:
    """AI 챗봇 서비스 클래스"""
    
    def __init__(
        self,
        provider: Literal["openai", "gemini"] = "gemini",
        model: Optional[str] = None,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        session_id: Optional[str] = None,
        storage_dir: Optional[str] = None
    ):
        """
        ChatService 초기화
        
        Args:
            provider: AI 제공자 ("openai" 또는 "gemini")
            model: 사용할 모델명 (None이면 기본값 사용)
            temperature: 생성 온도 (0.0 ~ 1.0)
            system_prompt: 시스템 프롬프트
            session_id: 세션 ID (대화 히스토리 저장용)
            storage_dir: 대화 히스토리 저장 디렉토리
        """
        self.provider = provider or os.getenv("AI_PROVIDER", "gemini")
        self.temperature = temperature
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        self.session_id = session_id or self._generate_session_id()
        
        # 저장 디렉토리 설정
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            # 기본: backend/chat_history/
            backend_dir = Path(__file__).parent.parent
            self.storage_dir = backend_dir / "chat_history"
        
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # LLM 초기화
        self.llm = self._initialize_llm(model)
        
        # 대화 히스토리
        self.chat_history: List[Message] = []
        
        # 저장된 대화 히스토리 로드
        self._load_history()
        
        # 프롬프트 템플릿 생성
        self.prompt = self._create_prompt_template()
        
        # Chain 생성
        self.chain = self._create_chain()
    
    def _generate_session_id(self) -> str:
        """세션 ID 생성"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_history_file_path(self) -> Path:
        """히스토리 파일 경로 반환"""
        return self.storage_dir / f"chat_{self.session_id}.json"
    
    def _load_history(self):
        """저장된 대화 히스토리 로드"""
        history_file = self._get_history_file_path()
        
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # JSON을 Message 객체로 변환
                self.chat_history = [
                    Message(
                        role=msg['role'],
                        content=msg['content'],
                        timestamp=msg.get('timestamp')
                    )
                    for msg in data.get('messages', [])
                ]
                
                print(f"✅ 대화 히스토리 로드 완료: {len(self.chat_history)}개 메시지")
            except Exception as e:
                print(f"⚠️ 대화 히스토리 로드 실패: {str(e)}")
                self.chat_history = []
        else:
            print(f"📝 새로운 대화 세션 시작: {self.session_id}")
    
    def _save_history(self):
        """대화 히스토리를 파일에 저장"""
        history_file = self._get_history_file_path()
        
        try:
            # Message 객체를 딕셔너리로 변환
            messages_dict = [
                {
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.timestamp
                }
                for msg in self.chat_history
            ]
            
            data = {
                'session_id': self.session_id,
                'provider': self.provider,
                'created_at': self.chat_history[0].timestamp if self.chat_history else datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'message_count': len(self.chat_history),
                'messages': messages_dict
            }
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # print(f"💾 대화 히스토리 저장 완료: {len(self.chat_history)}개 메시지")
        except Exception as e:
            print(f"⚠️ 대화 히스토리 저장 실패: {str(e)}")
    
    def _get_default_system_prompt(self) -> str:
        """기본 시스템 프롬프트 반환"""
        return """당신은 주식 포트폴리오 분석 전문가입니다.
사용자의 포트폴리오 데이터를 분석하고, 투자 전략에 대한 조언을 제공합니다.

주요 역할:
1. 포트폴리오 수익률 분석
2. 자산 배분 조언
3. 위험 관리 전략 제안
4. 투자 성과 평가

항상 친절하고 전문적인 답변을 제공하며, 투자 조언은 참고용임을 명시합니다."""
    
    def _initialize_llm(self, model: Optional[str]):
        """LLM 초기화"""
        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
            
            model_name = model or "gpt-4o-mini"
            return ChatOpenAI(
                api_key=api_key,
                model=model_name,
                temperature=self.temperature
            )
        
        elif self.provider == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY가 설정되지 않았습니다.")
            
            # Gemini 2.5 Flash 모델 사용
            model_name = model or "gemini-2.0-flash-exp"
            return ChatGoogleGenerativeAI(
                google_api_key=api_key,
                model=model_name,
                temperature=self.temperature,
                convert_system_message_to_human=True  # 시스템 메시지 변환
            )
        
        else:
            raise ValueError(f"지원하지 않는 provider: {self.provider}")
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """프롬프트 템플릿 생성"""
        return ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
    
    def _create_chain(self):
        """LangChain Chain 생성"""
        return (
            {
                "chat_history": lambda x: self._format_chat_history(),
                "input": RunnablePassthrough()
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
    
    def _format_chat_history(self) -> List:
        """채팅 히스토리를 LangChain 메시지 형식으로 변환"""
        messages = []
        for msg in self.chat_history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                messages.append(SystemMessage(content=msg.content))
        return messages
    
    def chat(self, user_message: str) -> str:
        """
        사용자 메시지를 받아 AI 응답 생성
        
        Args:
            user_message: 사용자 입력 메시지
            
        Returns:
            AI 응답 메시지
        """
        # 사용자 메시지를 히스토리에 추가
        self.chat_history.append(Message(role="user", content=user_message))
        
        # AI 응답 생성
        response = self.chain.invoke(user_message)
        
        # AI 응답을 히스토리에 추가
        self.chat_history.append(Message(role="assistant", content=response))
        
        # 히스토리 저장
        self._save_history()
        
        return response
    
    async def achat(self, user_message: str) -> str:
        """
        비동기 채팅 (스트리밍 지원)
        
        Args:
            user_message: 사용자 입력 메시지
            
        Returns:
            AI 응답 메시지
        """
        # 사용자 메시지를 히스토리에 추가
        self.chat_history.append(Message(role="user", content=user_message))
        
        # AI 응답 생성
        response = await self.chain.ainvoke(user_message)
        
        # AI 응답을 히스토리에 추가
        self.chat_history.append(Message(role="assistant", content=response))
        
        # 히스토리 저장
        self._save_history()
        
        return response
    
    async def stream_chat(self, user_message: str):
        """
        스트리밍 방식으로 AI 응답 생성
        
        Args:
            user_message: 사용자 입력 메시지
            
        Yields:
            AI 응답 토큰
        """
        # 사용자 메시지를 히스토리에 추가
        self.chat_history.append(Message(role="user", content=user_message))
        
        # AI 응답을 스트리밍으로 생성
        full_response = ""
        async for chunk in self.chain.astream(user_message):
            full_response += chunk
            yield chunk
        
        # 완전한 응답을 히스토리에 추가
        self.chat_history.append(Message(role="assistant", content=full_response))
        
        # 히스토리 저장
        self._save_history()
    
    def clear_history(self):
        """채팅 히스토리 초기화"""
        self.chat_history.clear()
        # 파일도 삭제
        history_file = self._get_history_file_path()
        if history_file.exists():
            history_file.unlink()
            print(f"🗑️ 대화 히스토리 파일 삭제: {history_file.name}")
    
    def get_history(self) -> List[Dict[str, str]]:
        """채팅 히스토리 반환"""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in self.chat_history
        ]
    
    def get_session_info(self) -> Dict[str, Any]:
        """세션 정보 반환"""
        return {
            "session_id": self.session_id,
            "provider": self.provider,
            "message_count": len(self.chat_history),
            "storage_path": str(self._get_history_file_path()),
            "created_at": self.chat_history[0].timestamp if self.chat_history else None,
            "updated_at": self.chat_history[-1].timestamp if self.chat_history else None
        }
    
    @classmethod
    def list_sessions(cls, storage_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """저장된 모든 세션 목록 반환"""
        if storage_dir:
            storage_path = Path(storage_dir)
        else:
            backend_dir = Path(__file__).parent.parent
            storage_path = backend_dir / "chat_history"
        
        if not storage_path.exists():
            return []
        
        sessions = []
        for file in storage_path.glob("chat_*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sessions.append({
                        "session_id": data.get("session_id"),
                        "provider": data.get("provider"),
                        "message_count": data.get("message_count", 0),
                        "created_at": data.get("created_at"),
                        "updated_at": data.get("updated_at"),
                        "file_path": str(file)
                    })
            except Exception as e:
                print(f"⚠️ 세션 파일 로드 실패 ({file.name}): {str(e)}")
        
        # 최신순 정렬
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return sessions
    
    @classmethod
    def load_session(cls, session_id: str, storage_dir: Optional[str] = None, **kwargs):
        """특정 세션 로드"""
        return cls(session_id=session_id, storage_dir=storage_dir, **kwargs)
    
    def set_system_prompt(self, prompt: str):
        """시스템 프롬프트 변경"""
        self.system_prompt = prompt
        self.prompt = self._create_prompt_template()
        self.chain = self._create_chain()


class PortfolioAnalysisChat(ChatService):
    """포트폴리오 분석 특화 챗봇 (Document Loader 사용)"""
    
    def __init__(
        self,
        portfolio_data: Optional[Dict] = None,
        provider: Literal["openai", "gemini"] = "gemini",
        model: Optional[str] = None,
        temperature: float = 0.7,
        session_id: Optional[str] = None,
        storage_dir: Optional[str] = None
    ):
        """
        PortfolioAnalysisChat 초기화
        
        Args:
            portfolio_data: 포트폴리오 데이터
            provider: AI 제공자
            model: 사용할 모델명
            temperature: 생성 온도
            session_id: 세션 ID
            storage_dir: 저장 디렉토리
        """
        self.portfolio_data = portfolio_data
        self.portfolio_document: Optional[Document] = None
        self.portfolio_markdown_path: Optional[Path] = None
        
        # 포트폴리오 마크다운 문서 생성
        if portfolio_data:
            self._generate_portfolio_document()
        
        # 포트폴리오 데이터 기반 시스템 프롬프트 생성
        system_prompt = self._create_portfolio_system_prompt()
        
        super().__init__(
            provider=provider,
            model=model,
            temperature=temperature,
            system_prompt=system_prompt,
            session_id=session_id,
            storage_dir=storage_dir
        )
    
    def _generate_portfolio_document(self):
        """포트폴리오 마크다운 문서 생성"""
        try:
            from .portfolio_document import generate_portfolio_markdown, save_portfolio_markdown
            
            # 마크다운 문서 저장 경로
            backend_dir = Path(__file__).parent.parent
            docs_dir = backend_dir / "portfolio_docs"
            docs_dir.mkdir(parents=True, exist_ok=True)
            
            # 마크다운 파일 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            markdown_path = docs_dir / f"portfolio_{timestamp}.md"
            
            markdown_content = generate_portfolio_markdown(self.portfolio_data)
            
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            self.portfolio_markdown_path = markdown_path
            
            # Document 객체 생성
            self.portfolio_document = Document(
                page_content=markdown_content,
                metadata={
                    "source": "portfolio_data",
                    "type": "markdown",
                    "generated_at": timestamp
                }
            )
            
            print(f"✅ 포트폴리오 마크다운 문서 생성: {markdown_path}")
            
        except Exception as e:
            print(f"⚠️ 포트폴리오 문서 생성 실패: {str(e)}")
            self.portfolio_document = None
    
    def _create_portfolio_system_prompt(self) -> str:
        """포트폴리오 데이터 기반 시스템 프롬프트 생성"""
        base_prompt = """당신은 주식 포트폴리오 분석 전문가입니다.
사용자의 포트폴리오 데이터를 분석하고, 투자 전략에 대한 조언을 제공합니다.

주요 역할:
1. 포트폴리오 수익률 분석
2. 자산 배분 조언
3. 위험 관리 전략 제안
4. 투자 성과 평가

항상 친절하고 전문적인 답변을 제공하며, 투자 조언은 참고용임을 명시합니다."""
        
        if self.portfolio_document:
            # 마크다운 문서 내용을 시스템 프롬프트에 포함
            portfolio_info = f"""

아래는 사용자의 상세한 포트폴리오 데이터입니다:

---
{self.portfolio_document.page_content[:10000]}  
---

위 포트폴리오 데이터를 바탕으로 사용자의 질문에 답변해주세요.
데이터에 명시된 정확한 수치를 사용하여 답변하세요."""
            
            base_prompt += portfolio_info
        elif self.portfolio_data:
            # 문서 생성 실패 시 요약 정보만 사용
            summary = self.portfolio_data.get("portfolio_summary", {})
            if summary:
                total_value = summary.get("total_value", 0)
                total_investment = summary.get("total_investment", 0)
                total_gain_loss = summary.get("total_gain_loss", 0)
                total_gain_loss_rate = summary.get("total_gain_loss_rate", 0)
                
                portfolio_info = f"""

현재 사용자의 포트폴리오 요약:
- 총 평가액: ₩{total_value:,.0f}
- 총 투자금: ₩{total_investment:,.0f}
- 총 손익: ₩{total_gain_loss:,.0f} ({total_gain_loss_rate:.2f}%)

이 정보를 바탕으로 사용자의 질문에 답변해주세요."""
                
                base_prompt += portfolio_info
        
        return base_prompt
    
    def update_portfolio_data(self, portfolio_data: Dict):
        """포트폴리오 데이터 업데이트"""
        self.portfolio_data = portfolio_data
        
        # 마크다운 문서 재생성
        self._generate_portfolio_document()
        
        # 시스템 프롬프트 업데이트
        self.set_system_prompt(self._create_portfolio_system_prompt())
    
    def analyze_portfolio(self) -> str:
        """포트폴리오 전체 분석"""
        if not self.portfolio_data:
            return "포트폴리오 데이터가 없습니다."
        
        analysis_prompt = """현재 포트폴리오를 전체적으로 분석해주세요.
다음 항목들을 포함해서 분석해주세요:
1. 전체 수익률 평가
2. 자산 배분 현황
3. 주요 보유 종목 분석
4. 리스크 평가
5. 개선 제안"""
        
        return self.chat(analysis_prompt)
    
    def get_investment_advice(self, question: str) -> str:
        """투자 조언 제공"""
        return self.chat(question)

