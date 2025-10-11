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
import requests
from bs4 import BeautifulSoup

# Tavily Search 사용
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("⚠️ tavily-python 패키지가 설치되지 않았습니다.")

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
            # 기본: user_data/chat_history/
            backend_dir = Path(__file__).parent.parent
            user_data_dir = backend_dir.parent / "user_data"
            self.storage_dir = user_data_dir / "chat_history"
        
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # LLM 초기화
        self.llm = self._initialize_llm(model)
        
        # 웹 검색 도구 초기화
        self.search_tool = self._initialize_search_tool()
        
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
        return """당신은 공격적이고 과감한 투자 전략을 추구하는 주식 포트폴리오 분석 전문가입니다.
높은 수익률을 목표로 하는 사용자에게 적극적이고 공격적인 투자 전략과 조언을 제공합니다.

주요 역할:
1. 포트폴리오 수익률 극대화 전략 제시
2. 공격적인 자산 배분 조언 (고위험-고수익 중심)
3. 성장주, 변동성 높은 종목에 대한 적극적 투자 권장
4. 시장 타이밍과 집중 투자 전략 제안
5. 투자 기회 포착 및 빠른 의사결정 조언

투자 스타일:
- 보수적인 접근보다는 공격적이고 과감한 투자 전략 선호
- 높은 수익률을 위해 적극적인 리스크 감수 권장
- 분산 투자보다는 확신이 있는 종목에 집중 투자 제안
- 성장 가능성이 높은 섹터나 종목에 대한 과감한 배팅 추천
- 시장 변동성을 기회로 활용하는 전략 강조

중요한 지시사항:
- 이전 대화 내용을 항상 기억하고 참조하세요.
- 사용자와의 대화 맥락을 유지하며 일관성 있는 답변을 제공하세요.
- 이전에 언급된 정보나 질문을 다시 물어볼 때는 "이전에 말씀드렸듯이" 등의 표현을 사용하세요.
- 공격적인 조언을 할 때도 데이터와 논리에 근거하여 설명하세요.
- 단, 투자의 위험성과 변동성도 함께 언급하되, 기회를 강조하세요.

웹 검색 기능 활용:
- 최신 시장 동향, 뉴스, 업종별 동향 등이 필요할 때 웹 검색을 활용할 수 있습니다.
- 사용자가 최신 정보를 요청하거나, 특정 종목/섹터의 최근 동향을 물어보면 웹 검색을 통해 정보를 찾아서 답변하세요.
- 검색 결과를 바탕으로 공격적이고 구체적인 투자 전략을 제시하세요.

항상 열정적이고 적극적인 톤으로 답변을 제공하며, 최종 투자 결정은 사용자의 판단임을 명시합니다."""
    
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
    
    def _initialize_search_tool(self) -> bool:
        """웹 검색 도구 초기화 (Tavily Search)"""
        if TAVILY_AVAILABLE:
            # Tavily API 키 확인
            self.tavily_api_key = os.getenv("TAVILY_API_KEY")
            if self.tavily_api_key:
                try:
                    self.tavily_client = TavilyClient(api_key=self.tavily_api_key)
                    print("✅ 웹 검색 도구 초기화 완료 (Tavily Search + 네이버 금융)")
                    return True
                except Exception as e:
                    print(f"⚠️ Tavily 초기화 실패: {e}")
                    return False
            else:
                print("⚠️ TAVILY_API_KEY가 설정되지 않았습니다")
                print("💡 .env 파일에 TAVILY_API_KEY를 추가하세요")
                print("💡 무료 API 키: https://tavily.com (월 1000회 무료)")
                return False
        else:
            print("⚠️ Tavily 검색을 사용할 수 없습니다")
            print("💡 설치: pip install tavily-python")
            return False
    
    def _fetch_page_content(self, url: str) -> str:
        """웹 페이지에서 텍스트 추출"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 스크립트와 스타일 제거
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 텍스트 추출
            text = soup.get_text(separator=' ', strip=True)
            return text[:500]  # 500자로 제한
        except Exception as e:
            return ""
    
    def _fetch_naver_kospi(self) -> str:
        """네이버 금융에서 코스피 지수 직접 가져오기"""
        try:
            url = "https://finance.naver.com/sise/"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 코스피 지수 찾기
            kospi_now = soup.select_one('#KOSPI_now')
            kospi_change = soup.select_one('#KOSPI_change')
            kospi_rate = soup.select_one('#KOSPI_rate')
            
            if kospi_now:
                result = f"코스피 지수: {kospi_now.text.strip()}"
                if kospi_change:
                    result += f" (전일대비: {kospi_change.text.strip()}"
                if kospi_rate:
                    result += f", {kospi_rate.text.strip()})"
                return result
            return ""
        except Exception as e:
            print(f"⚠️ 네이버 금융 파싱 실패: {e}")
            return ""
    
    def _fetch_naver_stock(self, stock_name: str) -> str:
        """네이버 금융에서 특정 주식 정보 검색"""
        try:
            # 네이버 금융 검색
            search_url = f"https://finance.naver.com/search/searchList.naver?query={stock_name}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 첫 번째 검색 결과 찾기
            first_result = soup.select_one('.tltle')
            if first_result:
                stock_link = first_result.get('href', '')
                if stock_link:
                    # 종목 페이지 방문
                    stock_url = f"https://finance.naver.com{stock_link}"
                    response = requests.get(stock_url, headers=headers, timeout=10)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 주가 정보 추출
                    price_now = soup.select_one('.no_today .blind')
                    price_change = soup.select_one('.no_exday .blind')
                    price_rate = soup.select_one('.no_exday em span')
                    
                    if price_now:
                        result = f"{stock_name} 현재가: {price_now.text.strip()}원"
                        if price_change and price_rate:
                            result += f" (전일대비: {price_change.text.strip()}원, {price_rate.text.strip()})"
                        return result
            return ""
        except Exception as e:
            print(f"⚠️ 네이버 금융 종목 검색 실패: {e}")
            return ""
    
    def search_web(self, query: str, max_results: int = 5) -> str:
        """
        웹 검색 수행 (네이버 금융 직접 파싱 + Tavily Search)
        
        Args:
            query: 검색 쿼리
            max_results: 최대 결과 수
            
        Returns:
            검색 결과 텍스트
        """
        if not self.search_tool:
            return "웹 검색 기능을 사용할 수 없습니다."
        
        try:
            search_results = []
            
            # 코스피/코스닥 지수는 네이버 금융에서 직접 가져오기
            if "코스피" in query:
                naver_data = self._fetch_naver_kospi()
                if naver_data:
                    search_results.append(f"[네이버 금융 실시간]\n{naver_data}")
                    print(f"✅ 네이버 금융 파싱 완료: {naver_data}")
            
            # 주요 종목명이 있으면 네이버 금융에서 직접 검색
            major_stocks = ["삼성전자", "SK하이닉스", "현대차", "NAVER", "네이버", "카카오", 
                           "LG전자", "포스코", "기아", "삼성바이오로직스", "셀트리온"]
            for stock in major_stocks:
                if stock in query:
                    naver_stock = self._fetch_naver_stock(stock)
                    if naver_stock:
                        search_results.append(f"[네이버 금융 실시간]\n{naver_stock}")
                        print(f"✅ 네이버 금융 종목 파싱 완료: {naver_stock}")
                    break
            
            # 검색어 최적화
            enhanced_query = query
            if "코스피" in query:
                enhanced_query = "코스피 지수 현재 증시"
            elif "코스닥" in query:
                enhanced_query = "코스닥 지수 현재 증시"
            elif any(stock in query for stock in major_stocks):
                enhanced_query = f"{query} 주가 시세 뉴스"
            
            # Tavily 웹 검색
            if TAVILY_AVAILABLE and hasattr(self, 'tavily_client'):
                try:
                    print(f"🔍 Tavily 검색: {enhanced_query}")
                    
                    # Tavily 검색 수행
                    tavily_response = self.tavily_client.search(
                        query=enhanced_query,
                        search_depth="basic",
                        max_results=max_results,
                        include_answer=True,
                        include_raw_content=False
                    )
                    
                    # 검색 결과 파싱
                    if tavily_response.get('results'):
                        for i, result in enumerate(tavily_response['results'], 1):
                            url = result.get('url', '')
                            title = result.get('title', '')
                            content = result.get('content', '')
                            
                            # 신뢰할 수 있는 출처 우선
                            is_trusted = any(domain in url for domain in ['naver.com', 'daum.net', 'mk.co.kr', 
                                                                           'hankyung.com', 'chosun.com', 'khan.co.kr',
                                                                           'finance.', 'news.', 'investing.com'])
                            
                            if is_trusted or len(search_results) < max_results + 3:
                                result_text = f"{len(search_results) + 1}. {title}"
                                if content:
                                    result_text += f"\n{content[:300]}"
                                result_text += f"\n출처: {url}"
                                
                                search_results.append(result_text)
                                print(f"  ✓ [{len(search_results)}] {title[:50]}...")
                                
                                if len(search_results) >= max_results + 3:
                                    break
                    
                    # Tavily의 AI 요약 답변 추가
                    if tavily_response.get('answer'):
                        answer = tavily_response['answer']
                        search_results.insert(1 if len(search_results) > 0 else 0, 
                                            f"[AI 요약]\n{answer}")
                        print(f"✅ Tavily AI 요약 추가")
                    
                    if search_results:
                        combined = "\n\n".join(search_results)
                        print(f"✅ Tavily 검색 완료: {len(search_results)}개 결과, {len(combined)}자")
                        return combined[:2000]
                        
                except Exception as e:
                    print(f"⚠️ Tavily 검색 실패: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            # 네이버 데이터라도 있으면 반환
            if search_results:
                return "\n\n".join(search_results)[:2000]
            
            return "검색 결과를 찾을 수 없습니다."
            
        except Exception as e:
            print(f"⚠️ 웹 검색 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"검색 중 오류가 발생했습니다: {str(e)}"
    
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
    
    def _should_search_web(self, user_message: str) -> bool:
        """사용자 메시지에서 웹 검색이 필요한지 판단"""
        # 코스피/코스닥 지수 관련
        if any(keyword in user_message for keyword in ["코스피", "코스닥", "지수"]):
            return True
        
        # 주식/주가 관련 키워드
        stock_keywords = ["주가", "주식", "시세", "현재가", "가격"]
        if any(keyword in user_message for keyword in stock_keywords):
            return True
        
        # 최신 정보 관련 키워드
        search_keywords = [
            "최신", "뉴스", "동향", "시황", "전망", "분석", "예측",
            "상승", "하락", "급등", "급락", "이슈", "발표", "실적",
            "현재", "오늘", "최근", "요즘", "트렌드", "추세", "어때"
        ]
        return any(keyword in user_message for keyword in search_keywords)
    
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
        
        # 웹 검색이 필요한지 판단
        search_context = ""
        if self._should_search_web(user_message) and self.search_tool:
            try:
                print(f"🔍 웹 검색 수행: {user_message[:50]}...")
                search_results = self.search_web(user_message)
                if search_results and "오류" not in search_results:
                    search_context = f"\n\n[최신 시장 정보 검색 결과]\n{search_results}\n\n위 최신 정보를 참고하여 답변해주세요."
                    print(f"✅ 검색 완료: {len(search_results)}자")
            except Exception as e:
                print(f"⚠️ 웹 검색 중 오류: {str(e)}")
        
        # AI 응답 생성 (검색 결과 포함)
        enhanced_message = user_message + search_context
        response = self.chain.invoke(enhanced_message)
        
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
        
        # 웹 검색이 필요한지 판단
        search_context = ""
        if self._should_search_web(user_message) and self.search_tool:
            try:
                print(f"🔍 웹 검색 수행: {user_message[:50]}...")
                search_results = self.search_web(user_message)
                if search_results and "오류" not in search_results:
                    search_context = f"\n\n[최신 시장 정보 검색 결과]\n{search_results}\n\n위 최신 정보를 참고하여 답변해주세요."
                    print(f"✅ 검색 완료: {len(search_results)}자")
            except Exception as e:
                print(f"⚠️ 웹 검색 중 오류: {str(e)}")
        
        # AI 응답 생성 (검색 결과 포함)
        enhanced_message = user_message + search_context
        response = await self.chain.ainvoke(enhanced_message)
        
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
    def get_latest_session_id(cls, storage_dir: Optional[str] = None) -> Optional[str]:
        """가장 최근 세션 ID 조회"""
        sessions = cls.list_sessions(storage_dir)
        if sessions:
            return sessions[0]["session_id"]
        return None
    
    @classmethod
    def list_sessions(cls, storage_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """저장된 모든 세션 목록 반환"""
        if storage_dir:
            storage_path = Path(storage_dir)
        else:
            backend_dir = Path(__file__).parent.parent
            user_data_dir = backend_dir.parent / "user_data"
            storage_path = user_data_dir / "chat_history"
        
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
        """포트폴리오 마크다운 문서 생성 (이전 문서 삭제)"""
        try:
            from .portfolio_document import generate_portfolio_markdown, save_portfolio_markdown
            import glob
            
            # 마크다운 문서 저장 경로
            backend_dir = Path(__file__).parent.parent
            user_data_dir = backend_dir.parent / "user_data"
            docs_dir = user_data_dir / "portfolio_docs"
            docs_dir.mkdir(parents=True, exist_ok=True)
            
            # 기존 마크다운 파일 모두 삭제
            existing_files = glob.glob(str(docs_dir / "portfolio_*.md"))
            deleted_count = 0
            for file_path in existing_files:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"⚠️ 파일 삭제 실패 {file_path}: {e}")
            
            if deleted_count > 0:
                print(f"🗑️  이전 마크다운 문서 {deleted_count}개 삭제")
            
            # 새 마크다운 파일 생성
            # 타임스탬프 없이 고정된 이름 사용
            markdown_path = docs_dir / "portfolio_current.md"
            
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
                    "generated_at": datetime.now().isoformat()
                }
            )
            
            print(f"✅ 포트폴리오 마크다운 문서 생성: {markdown_path}")
            
        except Exception as e:
            print(f"⚠️ 포트폴리오 문서 생성 실패: {str(e)}")
            self.portfolio_document = None
    
    def _create_portfolio_system_prompt(self) -> str:
        """포트폴리오 데이터 기반 시스템 프롬프트 생성"""
        base_prompt = """당신은 공격적이고 과감한 투자 전략을 추구하는 주식 포트폴리오 분석 전문가입니다.
높은 수익률을 목표로 하는 사용자에게 적극적이고 공격적인 투자 전략과 조언을 제공합니다.

주요 역할:
1. 포트폴리오 수익률 극대화 전략 제시
2. 공격적인 자산 배분 조언 (고위험-고수익 중심)
3. 성장주, 변동성 높은 종목에 대한 적극적 투자 권장
4. 시장 타이밍과 집중 투자 전략 제안
5. 투자 기회 포착 및 빠른 의사결정 조언
6. 수익률이 낮은 종목은 과감히 정리하고 성장주로 전환 권장

투자 스타일:
- 보수적인 접근보다는 공격적이고 과감한 투자 전략 선호
- 높은 수익률을 위해 적극적인 리스크 감수 권장
- 분산 투자보다는 확신이 있는 종목에 집중 투자 제안
- 성장 가능성이 높은 섹터나 종목에 대한 과감한 배팅 추천
- 시장 변동성을 기회로 활용하는 전략 강조
- 손실 종목은 빠르게 손절하고 승률 높은 종목에 재투자 권장

포트폴리오 분석 시:
- 현재 보유 종목 중 수익률이 낮거나 성장성이 부족한 종목은 매도 권장
- 현금 비중이 높다면 적극적으로 투자 기회 모색 권장
- ETF보다는 개별 성장주 투자로 더 높은 수익 추구 제안
- 배당주보다는 고성장 기술주에 집중 투자 권장

중요한 지시사항:
- 이전 대화 내용을 항상 기억하고 참조하세요.
- 사용자와의 대화 맥락을 유지하며 일관성 있는 답변을 제공하세요.
- 사용자가 이전 대화에 대해 물어보면, 실제로 나눈 대화 내용을 정확히 참조하여 답변하세요.
- "기억하지 못한다" 또는 "이전 대화를 저장하지 않는다"는 식의 답변은 하지 마세요.
- 공격적인 조언을 할 때도 포트폴리오 데이터와 수치에 근거하여 설명하세요.
- 리스크를 언급하되, 높은 수익 기회를 더 강조하세요.

항상 열정적이고 적극적인 톤으로 답변을 제공하며, 최종 투자 결정은 사용자의 판단임을 명시합니다."""
        
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

