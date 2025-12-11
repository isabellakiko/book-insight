"""Data models for book analysis."""

from pydantic import BaseModel


class Chapter(BaseModel):
    """Chapter structure."""
    index: int
    title: str
    start: int
    end: int


class ChapterAnalysis(BaseModel):
    """Chapter analysis result."""
    chapter_index: int
    title: str
    summary: str
    characters: list[str] = []
    events: list[str] = []
    sentiment: str = ""
    keywords: list[str] = []


class Character(BaseModel):
    """Character model (legacy, will be removed)."""
    id: str
    name: str
    aliases: list[str] = []
    description: str = ""
    first_appearance: int = 0
    role: str = "minor"  # protagonist/antagonist/supporting/minor
    attributes: dict = {}


# ===== 新的人物按需分析模型 =====

class CharacterInteraction(BaseModel):
    """人物互动记录（结构化）"""
    character: str                    # 互动对象姓名
    type: str = "interaction"         # dialogue/conflict/cooperation/support/observation
    description: str = ""             # 具体互动内容
    sentiment: str = "neutral"        # positive/neutral/negative - 互动的情感基调
    initiated_by: str = ""            # 谁发起：target/other/mutual


class CharacterAppearance(BaseModel):
    """人物在某章节的出现信息"""
    chapter_index: int
    chapter_title: str
    # 基础信息
    events: list[str] = []            # 该人物参与的事件（最多5个）
    interactions: list[CharacterInteraction] = []  # 结构化互动记录
    quote: str = ""                   # 该人物的代表性台词（原话）
    # 第一人称视角分析
    narrator_bias: str = ""           # 张成对该人物态度：positive/neutral/negative/unclear
    # 章节分析
    emotional_state: str = ""         # 该人物在本章的情感/心理状态
    chapter_significance: str = ""    # 本章对人物发展的重要性：low/medium/high
    mentioned_characters: list[str] = []  # 本章中与该人物相关的所有人物
    key_moment: str = ""              # 本章最能体现该人物的关键时刻
    # 出场类型标记
    is_mentioned_only: bool = False   # True = 仅被提及，无实际出场（events 和 interactions 均为空）


class CharacterRelation(BaseModel):
    """人物关系"""
    target_name: str                  # 关系对象
    relation_type: str                # friend/enemy/lover/family/mentor/rival/complex
    description: str                  # 关系描述（基于客观行为）
    evidence_chapters: list[int] = [] # 证据章节
    # 新增：关系分析增强
    objective_basis: str = ""         # 客观判断依据（具体行为/对话）
    first_interaction_chapter: int = -1  # 首次互动章节
    relation_evolution: str = ""      # 关系演变简述（如有变化）
    confidence: str = "medium"        # 判断可信度：high/medium/low


class CharacterSearchResult(BaseModel):
    """人物搜索结果（快速返回）"""
    name: str
    found_in_chapters: list[int]     # 出现的章节索引
    chapter_titles: list[str]        # 章节标题
    total_mentions: int              # 总提及次数


class CharacterTrait(BaseModel):
    """性格特征（带证据）"""
    trait: str                       # 特征名称
    description: str                 # 描述
    evidence: list[str] | str = []   # 支撑证据


class DetailedCharacter(BaseModel):
    """详细人物分析结果"""
    name: str
    aliases: list[str] = []

    # 基本信息
    description: str = ""            # 人物简介
    role: str = "unknown"            # protagonist/antagonist/supporting/minor
    personality: list[str] = []      # 性格特点（简单列表）

    # 新增：深度性格分析
    summary: str = ""                # 一句话总结
    growth_arc: str = ""             # 成长轨迹
    core_traits: list[CharacterTrait] = []  # 核心性格特征（带证据）
    strengths: list[str] = []        # 优点
    weaknesses: list[str] = []       # 缺点
    notable_quotes: list[str] = []   # 经典语录

    # 出现章节
    appearances: list[CharacterAppearance] = []
    first_appearance: int = -1       # 首次出场章节
    last_appearance: int = -1        # 最后出场章节
    total_chapters: int = 0          # 出现章节总数
    total_analyzed_chapters: int = 0 # 已分析章节数

    # 人物关系
    relations: list[CharacterRelation] = []

    # 分析状态
    analysis_status: str = "pending"  # pending/searching/analyzing/completed/error
    analyzed_chapters: list[int] = [] # 已分析的章节
    error_message: str = ""

    # 分析元数据（新增）
    analysis_confidence: str = ""     # 整体分析可信度：high/medium/low
    analysis_limitations: str = ""    # 分析局限性说明
    discovered_characters: list[str] = []  # 分析过程中发现的关联人物（供后续分析）


class Event(BaseModel):
    """Event/plot point model."""
    id: str
    chapter: int
    title: str
    summary: str
    characters: list[str] = []
    location: str = ""
    importance: int = 1  # 1-5
    tags: list[str] = []


class Relation(BaseModel):
    """Character relationship."""
    source: str
    target: str
    type: str  # friend/enemy/lover/family/mentor/...
    description: str = ""
    evidence: list[str] = []
    chapters: list[int] = []
