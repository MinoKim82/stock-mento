"""
LangChain을 활용한 AI 챗봇 서비스
OpenAI GPT와 Google Gemini를 지원합니다.
"""
import os
from typing import List, Dict, Optional, Literal
from dataclasses import dataclass
from dotenv import load_dotenv

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# .env 파일 로드
load_dotenv()

@dataclass
class Message:
    """채팅 메시지 데이터 클래스"""
    role: Literal["user", "assistant", "system"]
    content: str

class ChatService:
    """AI 챗봇 서비스 클래스"""
    
    def __init__(
        self,
        provider: Literal["openai", "gemini"] = "gemini",
        model: Optional[str] = None,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ):
        """
        ChatService 초기화
        
        Args:
            provider: AI 제공자 ("openai" 또는 "gemini")
            model: 사용할 모델명 (None이면 기본값 사용)
            temperature: 생성 온도 (0.0 ~ 1.0)
            system_prompt: 시스템 프롬프트
        """
        self.provider = provider or os.getenv("AI_PROVIDER", "gemini")
        self.temperature = temperature
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        
        # LLM 초기화
        self.llm = self._initialize_llm(model)
        
        # 대화 히스토리
        self.chat_history: List[Message] = []
        
        # 프롬프트 템플릿 생성
        self.prompt = self._create_prompt_template()
        
        # Chain 생성
        self.chain = self._create_chain()
    
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
            
            model_name = model or "gemini-1.5-flash"
            return ChatGoogleGenerativeAI(
                google_api_key=api_key,
                model=model_name,
                temperature=self.temperature
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
    
    def clear_history(self):
        """채팅 히스토리 초기화"""
        self.chat_history.clear()
    
    def get_history(self) -> List[Dict[str, str]]:
        """채팅 히스토리 반환"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.chat_history
        ]
    
    def set_system_prompt(self, prompt: str):
        """시스템 프롬프트 변경"""
        self.system_prompt = prompt
        self.prompt = self._create_prompt_template()
        self.chain = self._create_chain()


class PortfolioAnalysisChat(ChatService):
    """포트폴리오 분석 특화 챗봇"""
    
    def __init__(
        self,
        portfolio_data: Optional[Dict] = None,
        provider: Literal["openai", "gemini"] = "gemini",
        model: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        PortfolioAnalysisChat 초기화
        
        Args:
            portfolio_data: 포트폴리오 데이터
            provider: AI 제공자
            model: 사용할 모델명
            temperature: 생성 온도
        """
        self.portfolio_data = portfolio_data
        
        # 포트폴리오 데이터 기반 시스템 프롬프트 생성
        system_prompt = self._create_portfolio_system_prompt()
        
        super().__init__(
            provider=provider,
            model=model,
            temperature=temperature,
            system_prompt=system_prompt
        )
    
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
        
        if self.portfolio_data:
            # 포트폴리오 요약 정보 추가
            summary = self.portfolio_data.get("portfolio_summary", {})
            if summary:
                total_value = summary.get("total_value", 0)
                total_investment = summary.get("total_investment", 0)
                total_gain_loss = summary.get("total_gain_loss", 0)
                total_gain_loss_rate = summary.get("total_gain_loss_rate", 0)
                
                portfolio_info = f"""

현재 사용자의 포트폴리오 정보:
- 총 평가액: ₩{total_value:,.0f}
- 총 투자금: ₩{total_investment:,.0f}
- 총 손익: ₩{total_gain_loss:,.0f} ({total_gain_loss_rate:.2f}%)

이 정보를 바탕으로 사용자의 질문에 답변해주세요."""
                
                base_prompt += portfolio_info
        
        return base_prompt
    
    def update_portfolio_data(self, portfolio_data: Dict):
        """포트폴리오 데이터 업데이트"""
        self.portfolio_data = portfolio_data
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

