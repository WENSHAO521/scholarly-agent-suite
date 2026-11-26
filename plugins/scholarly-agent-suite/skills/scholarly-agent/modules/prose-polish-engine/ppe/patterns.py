"""Catalog of templated phrasing patterns, by language.

Mirrors references/pattern-catalog.md (English, and the category scheme
every language shares), references/chinese-academic-prose.md (Chinese), and
references/other-languages.md (Japanese, Korean, Spanish, French, German,
Portuguese, Russian, and how to polish a language with no catalog here). Each pattern names a
category from ppe.CATEGORIES and a severity:

- ``remove``  never belongs in a manuscript (chat residue).
- ``revise``  almost always a template; rewrite it so the sentence says
              something specific, or delete it.
- ``watch``   legitimate in moderation; flag only when it recurs or does no
              work in its sentence.

Defensive writing (hedges that answer to no evidence, pre-emptive
caveats, disclaimers, apologetic framing, over-justification) has its own
categories; see references/defensive-writing.md. A match there is a
question for the polisher (what evidence does this qualifier answer to?),
never an instruction to delete a hedge the evidence needs.

Chinese patterns list Traditional and Simplified forms together. The
catalog is deliberately small and literal: it names phrasing an editor
would mark, not a statistical model of anything.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Pattern:
    id: str
    lang: str
    category: str
    severity: str
    regex: str
    hint: str

    def compiled(self) -> "re.Pattern[str]":
        flags = 0 if self.lang in ("zh", "ja", "ko") else re.IGNORECASE
        return re.compile(self.regex, flags)


def _p(id, lang, category, severity, regex, hint):
    return Pattern(id, lang, category, severity, regex, hint)


EN_PATTERNS: List[Pattern] = [
    # chat residue: text addressed to a chat user, never to a reader
    _p("en-residue-certainly", "en", "chat-residue", "remove",
       r"^\s*(certainly|sure|absolutely|of course)[!,.]", "delete the reply-to-a-request opener"),
    _p("en-residue-hope-helps", "en", "chat-residue", "remove",
       r"\bI hope this helps\b|\blet me know if you\b|\bfeel free to\b", "delete; addressed to a chat user"),
    _p("en-residue-here-is", "en", "chat-residue", "remove",
       r"\bhere is (a|the|your) (revised|polished|rewritten|improved) (version|text|paragraph)\b", "delete"),
    _p("en-residue-as-an-ai", "en", "chat-residue", "remove",
       r"\bas an AI( language model)?\b|\bas a large language model\b", "delete"),
    # stock connectives
    _p("en-conn-furthermore", "en", "stock-connective", "watch", r"\bfurthermore\b",
       "name the actual relation or drop it"),
    _p("en-conn-moreover", "en", "stock-connective", "watch", r"\bmoreover\b",
       "name the actual relation or drop it"),
    _p("en-conn-additionally", "en", "stock-connective", "watch", r"\badditionally\b",
       "usually droppable; the next sentence already adds"),
    _p("en-conn-in-addition", "en", "stock-connective", "watch", r"\bin addition\b", "usually droppable"),
    _p("en-conn-notably", "en", "stock-connective", "watch", r"^\s*notably,", "say why it is notable or drop it"),
    _p("en-conn-importantly", "en", "stock-connective", "watch", r"^\s*(more )?importantly,",
       "show the importance in the claim itself"),
    # empty emphasis
    _p("en-emph-important-to-note", "en", "empty-emphasis", "revise",
       r"\bit is (important|worth|crucial|essential) (to note|noting|to highlight|to emphasi[sz]e) that\b",
       "delete the frame and state the point"),
    _p("en-emph-crucial-role", "en", "empty-emphasis", "revise",
       r"\bplays? an? (crucial|pivotal|vital|key|significant|important) role\b",
       "say what it does, by which mechanism"),
    _p("en-emph-cannot-overstate", "en", "empty-emphasis", "revise",
       r"\bcannot be overstated\b|\bof paramount importance\b", "state the stake instead"),
    _p("en-emph-underscore", "en", "empty-emphasis", "watch", r"\bunderscores?\b|\bunderscoring\b",
       "'shows', 'means', or the specific implication"),
    # inflated vocabulary
    _p("en-vocab-delve", "en", "inflated-vocabulary", "revise", r"\bdelv(e|es|ed|ing)\b",
       "'examine', 'ask', or the specific operation"),
    _p("en-vocab-tapestry", "en", "inflated-vocabulary", "revise",
       r"\b(rich |intricate |complex )?tapestry\b|\bintricate interplay\b", "name the parts and how they relate"),
    _p("en-vocab-landscape", "en", "inflated-vocabulary", "revise",
       r"\b(ever-(changing|evolving)|evolving|dynamic|complex) landscape\b|\bthe landscape of\b",
       "name the field or the change"),
    _p("en-vocab-realm", "en", "inflated-vocabulary", "revise", r"\bin the (realm|domain|sphere) of\b",
       "'in' plus the field"),
    _p("en-vocab-multifaceted", "en", "inflated-vocabulary", "watch", r"\bmultifaceted\b|\bmulti-faceted\b",
       "list the facets that matter"),
    _p("en-vocab-pivotal", "en", "inflated-vocabulary", "watch", r"\bpivotal\b", "say what turns on it"),
    _p("en-vocab-showcase", "en", "inflated-vocabulary", "watch", r"\bshowcas(e|es|ed|ing)\b", "'show'"),
    _p("en-vocab-leverage", "en", "inflated-vocabulary", "watch", r"\bleverag(e|es|ed|ing)\b", "'use'"),
    _p("en-vocab-harness", "en", "inflated-vocabulary", "watch", r"\bharness(es|ed|ing)? the (power|potential)\b",
       "'use'"),
    _p("en-vocab-seamless", "en", "inflated-vocabulary", "watch", r"\bseamless(ly)?\b", "usually delete"),
    _p("en-vocab-navigate", "en", "inflated-vocabulary", "revise",
       r"\bnavigat(e|es|ed|ing) the (complexities|challenges|intricacies)\b", "name the difficulty"),
    _p("en-vocab-groundbreaking", "en", "inflated-vocabulary", "revise",
       r"\b(groundbreaking|game-changing|revolutioni[sz]e[sd]?|unprecedented)\b",
       "state the contribution at its real size"),
    # formulaic frames
    _p("en-frame-todays-world", "en", "formulaic-frame", "revise",
       r"\bin (today's|the modern|our) (rapidly )?(changing|evolving|fast-paced|digital|interconnected) (world|era|age|society)\b",
       "open with the specific problem"),
    _p("en-frame-aims-to", "en", "formulaic-frame", "watch",
       r"\bthis (study|paper|article|research) (aims|seeks|endeavou?rs) to\b", "'This article argues / shows / estimates'"),
    _p("en-frame-shed-light", "en", "formulaic-frame", "revise",
       r"\bsheds? (new )?light on\b|\bpaves? the way (for|to)\b|\bopens? (up )?new avenues\b",
       "say what is now known or possible"),
    _p("en-frame-valuable-insights", "en", "formulaic-frame", "revise",
       r"\b(provides?|offers?|yields?) (valuable|important|novel|key) insights?\b", "state the insight"),
    _p("en-frame-highlight-importance", "en", "formulaic-frame", "revise",
       r"\b(highlights?|underscores?|emphasi[sz]es) the (importance|significance|need) (of|for)\b",
       "state the consequence"),
    # stock summaries
    _p("en-sum-in-conclusion", "en", "stock-summary", "watch", r"^\s*in (conclusion|summary|sum),",
       "a heading usually does this job"),
    _p("en-sum-overall", "en", "stock-summary", "watch", r"^\s*(overall|to sum up|taken together|all in all),",
       "end on the paragraph's last real point"),
    # hedge stacks
    _p("en-hedge-stack", "en", "hedge-stack", "revise",
       r"\b(may|might|could) (potentially|possibly|perhaps|conceivably)\b|\bpossibly (may|might|could)\b",
       "one hedge, sized to the evidence"),
    _p("en-hedge-somewhat", "en", "hedge-stack", "watch", r"\bto (some|a certain) (extent|degree)\b",
       "say to what extent, or drop"),
    # contrast templates
    _p("en-contrast-not-only", "en", "contrast-template", "watch", r"\bnot only\b[^.;]{1,120}\bbut also\b",
       "fine once; a habit when it recurs"),
    _p("en-contrast-not-just", "en", "contrast-template", "revise",
       r"\b(it|this) is not (just|merely|only|simply) (about )?[^.;]{1,80}[,;] (it is|it's|but)\b",
       "state the positive claim directly"),
    # nominalization
    _p("en-nominal-of", "en", "nominalization", "watch",
       r"\bthe (implementation|utilization|examination|investigation|establishment|enhancement|facilitation) of\b",
       "use the verb"),
    _p("en-nominal-utilize", "en", "nominalization", "watch", r"\butili[sz](e|es|ed|ing|ation)\b", "'use'"),
    # defensive writing (references/defensive-writing.md)
    _p("en-def-could-be-argued", "en", "defensive-hedge", "revise",
       r"\bit (could|can|might|may) (perhaps |possibly )?be (argued|said|suggested|claimed|contended) that\b"
       r"|\bone (could|might|may) (perhaps )?(argue|say|suggest|contend) that\b",
       "make the argument and own it, or attribute it with a citation"),
    _p("en-def-seems-to-suggest", "en", "defensive-hedge", "revise",
       r"\b(seems?|appears?|tends?) to (suggest|indicate|imply)\b|\b(may|might|could) suggest (a |the )?(possible|potential)\b"
       r"|\bsuggests? (a |the )?(possible|potential)\b",
       "one qualifier, sized to the evidence: 'suggests' or 'may indicate'"),
    _p("en-def-not-impossible", "en", "defensive-hedge", "revise",
       r"\bit is not (impossible|inconceivable|unreasonable|implausible) (that|to)\b"
       r"|\bnot (entirely|altogether|wholly|completely) (without|unlike|unrelated)\b",
       "say how likely or how related, in positive terms"),
    _p("en-def-arguably", "en", "defensive-hedge", "watch",
       r"\barguably\b|\bin (a|some) (sense|ways?)\b|\bin a way\b|\bmore or less\b|\bsomewhat\b",
       "say in which sense or to what degree, or drop it"),
    _p("en-cav-limitations-opener", "en", "preemptive-caveat", "revise",
       r"\b(while|although|though|despite the fact that) (this|the present|our|the current) "
       r"(study|analysis|paper|article|research|approach|work) (has|had|is subject to|is not without|has its own) "
       r"((some|several|certain|a number of|its|obvious|clear) )?limitations\b",
       "state the limitation once, specifically, where it bears on a result"),
    _p("en-cav-should-be-noted", "en", "preemptive-caveat", "revise",
       r"\bit (should|must) be (noted|acknowledged|borne in mind|kept in mind|recogni[sz]ed|stressed|emphasi[sz]ed) that\b",
       "drop the frame; if it is a limitation, say what it limits"),
    _p("en-cav-interpret-caution", "en", "preemptive-caveat", "revise",
       r"\b(these|the|our|such) (results|findings|estimates|conclusions) (should|must|need to) be "
       r"(interpreted|treated|viewed|taken|read|considered) with (some |considerable |due |great |appropriate )?(caution|care)\b",
       "say which result, why, and which reading still holds"),
    _p("en-cav-further-research", "en", "preemptive-caveat", "revise",
       r"\b(further|more|additional|future) (research|work|studies|investigation) (is|are) (needed|required|warranted|necessary)\b"
       r"|\bno (definitive|firm|final) conclusions? can be drawn\b",
       "name the data or design that would settle it, or cut"),
    _p("en-cav-not-to-say", "en", "preemptive-caveat", "watch",
       r"\b(this|that) is not to (say|suggest|imply|claim) that\b",
       "keep only if it heads off a reading a reader would actually make"),
    _p("en-cav-admittedly", "en", "preemptive-caveat", "watch",
       r"^\s*(of course|admittedly|granted|to be sure|needless to say|that (being )?said),",
       "concede only what a reader would raise"),
    _p("en-disc-not-exhaustive", "en", "disclaimer", "revise",
       r"\b(is|are) (by no means|not intended to be|not meant to be|in no way) (an? )?(exhaustive|comprehensive|complete|definitive)\b"
       r"|\bdoes not (claim|purport|pretend|aim|attempt|seek) to (be|offer|provide|give) (an? )?(exhaustive|comprehensive|complete|definitive)\b"
       r"|\bmakes? no claims? (to|of) (completeness|comprehensiveness|exhaustiveness)\b",
       "state the actual scope in positive terms: what is covered, which period, which sources"),
    _p("en-disc-no-claim", "en", "disclaimer", "watch",
       r"\b(we|I|the authors?) (do|does) not (claim|wish to claim|intend to claim|mean to suggest|wish to suggest)\b|\bno claim is made\b",
       "keep if it rules out a reading readers would make (e.g. causality); cut if it rules out nothing"),
    _p("en-disc-beyond-scope", "en", "disclaimer", "watch",
       r"\b(is|are|lies|lie|falls?|remains?) (beyond|outside) the scope of (this|the present|the current) "
       r"(paper|study|article|review|chapter|work|analysis)\b",
       "fine once; repeated, it reads as fencing off the reader"),
    _p("en-apol-humble", "en", "apologetic-framing", "revise",
       r"\b(we|I) (humbly|modestly|tentatively|cautiously) (suggest|propose|submit|offer|argue|venture)\b"
       r"|\bin (my|our) (humble|modest) (opinion|view)\b|\b(we|I) apologi[sz]e\b|\bplease (forgive|excuse)\b",
       "state the claim at the size the evidence gives it"),
    _p("en-apol-modest-attempt", "en", "apologetic-framing", "revise",
       r"\b(modest|humble|small|tentative|limited|preliminary|rudimentary) (attempt|effort|endeavou?r|contribution)\b",
       "describe what the work contributes, without size words"),
    _p("en-apol-merely", "en", "apologetic-framing", "watch",
       r"\b(this|the present|our) (paper|study|article|work|chapter) (merely|simply|only|just) (aims|seeks|tries|attempts|hopes|wishes)\b"
       r"|\b(we|I) (try|attempt|endeavou?r) to\b",
       "say what you do: 'we estimate', not 'we try to estimate'"),
    _p("en-just-reasonable", "en", "over-justification", "revise",
       r"\bit (is|seems|appears) (therefore |thus |hence )?(reasonable|justified|fair|legitimate|safe|appropriate) to "
       r"(assume|argue|conclude|say|suggest|believe|expect)\b|\bthere is (good |every |some )?reason to believe\b",
       "give the reason itself, or state the claim"),
    _p("en-just-widely-accepted", "en", "over-justification", "revise",
       r"\bas is (widely|generally|commonly|well) (known|accepted|acknowledged|recogni[sz]ed|established)\b"
       r"|\bit is (widely|generally|commonly|well) (known|accepted|acknowledged|recogni[sz]ed|established) that\b",
       "the citation carries the point; drop the appeal to consensus"),
    _p("en-just-for-the-sake", "en", "over-justification", "revise",
       r"\bfor the sake of (rigou?r|completeness|transparency|thoroughness|robustness|caution)\b|\bto be on the safe side\b",
       "say what the step does; a standard step needs a citation, not a defence"),
    _p("en-just-ensure-rigor", "en", "over-justification", "watch",
       r"\b(in order )?to (ensure|guarantee|maximi[sz]e|enhance) the (rigou?r|robustness|reliability|validity|objectivity|credibility) of\b"
       r"|\b(carefully|rigorously|meticulously|thoroughly) (designed|selected|chosen|conducted|considered|controlled|validated)\b",
       "describe the procedure; adverbs do not make it rigorous"),
]

ZH_PATTERNS: List[Pattern] = [
    # chat residue
    _p("zh-residue-certainly", "zh", "chat-residue", "remove", r"^\s*(當然可以|当然可以|好的)[！!，,。]",
       "刪除：這是回覆請求的開場"),
    _p("zh-residue-hope-helps", "zh", "chat-residue", "remove",
       r"希望(這|这)(對|对)(你|您)有(所)?(幫助|帮助)|如有(其他|任何)(問題|问题|需要)", "刪除：對聊天對象說的話"),
    _p("zh-residue-here-is", "zh", "chat-residue", "remove",
       r"以下是(修改|潤色|润色|改寫|改写|優化|优化)(後|后)?的", "刪除"),
    _p("zh-residue-as-an-ai", "zh", "chat-residue", "remove",
       r"作為一?個?(AI|人工智慧|人工智能|語言模型)|作为一?个?(AI|人工智能|语言模型)", "刪除"),
    # stock connectives
    _p("zh-conn-ciwai", "zh", "stock-connective", "watch", r"此外[，,]", "說出真正的邏輯關係，或直接刪去"),
    _p("zh-conn-tongshi", "zh", "stock-connective", "watch", r"與此同時|与此同时", "多半只是「也」"),
    _p("zh-conn-zhide", "zh", "stock-connective", "revise", r"值得(注意|一提|關注|关注)的是",
       "刪去框架，直接陳述重點"),
    _p("zh-conn-zhichu", "zh", "stock-connective", "revise", r"需要(指出|強調|强调|說明|说明)的是",
       "刪去框架，直接陳述重點"),
    _p("zh-emph-burongzhiyi", "zh", "empty-emphasis", "revise",
       r"不可否認|不可否认|毋庸置疑|眾所周知|众所周知|顯而易見|显而易见", "學術文本少用；要嘛給證據，要嘛刪去"),
    # empty emphasis
    _p("zh-emph-yiyi", "zh", "empty-emphasis", "revise", r"具有(十分|非常|極其|极其)?重要(的)?(意義|意义|價值|价值)",
       "說明重要在哪裡、對誰重要"),
    _p("zh-emph-zuoyong", "zh", "empty-emphasis", "revise",
       r"(起|發揮|发挥)(著|着|了)?(至關重要|至关重要|關鍵|关键|重要|核心)(的)?作用", "說出它做了什麼、透過什麼機制"),
    _p("zh-emph-zhiguan", "zh", "empty-emphasis", "watch", r"至關重要|至关重要|不可或缺", "換成具體後果"),
    # inflated vocabulary (policy / marketing register in an academic text)
    _p("zh-vocab-funeng", "zh", "inflated-vocabulary", "revise", r"賦能|赋能", "說出具體提升了什麼能力"),
    _p("zh-vocab-zhuli", "zh", "inflated-vocabulary", "watch", r"助力", "「有助於」或具體動詞"),
    _p("zh-vocab-shendu", "zh", "inflated-vocabulary", "revise", r"深度融合|深度賦能|深度赋能|全方位|多維度|多维度",
       "說出哪些部分、怎樣結合"),
    _p("zh-vocab-jargon", "zh", "inflated-vocabulary", "revise", r"抓手|閉環|闭环|底層邏輯|底层逻辑|頂層設計|顶层设计",
       "政策或商業用語，換成學術上的具體說法"),
    _p("zh-vocab-dazao", "zh", "inflated-vocabulary", "watch", r"打造", "「建立」「設計」等具體動詞"),
    _p("zh-vocab-shenru", "zh", "inflated-vocabulary", "watch", r"深入(探討|探讨|研究|分析|剖析)",
       "「深入」多半可刪；說出探討了什麼"),
    # formulaic frames
    _p("zh-frame-suizhe", "zh", "formulaic-frame", "revise",
       r"隨著[^。，,]{1,30}的?(快速|迅速|不斷|飛速|蓬勃|日益)?(發展|進步|普及)|随着[^。，,]{1,30}的?(快速|迅速|不断|飞速|蓬勃|日益)?(发展|进步|普及)",
       "直接從具體問題開始"),
    _p("zh-frame-beijing", "zh", "formulaic-frame", "watch", r"在[^。，,]{1,20}的(大)?背景下", "背景若與論點無關就刪去"),
    _p("zh-frame-jinnian", "zh", "formulaic-frame", "watch", r"近年來|近年来", "給出時間或文獻，或刪去"),
    _p("zh-frame-zhizai", "zh", "formulaic-frame", "watch", r"本(文|研究)旨在", "「本文論證／估計／指出」"),
    _p("zh-frame-silu", "zh", "formulaic-frame", "revise",
       r"(為|为)[^。，,]{1,25}提供(了)?(新的|有益的|重要的)?(思路|視角|视角|參考|参考|借鑑|借鉴|啟示|启示)",
       "說出具體提供了什麼"),
    _p("zh-frame-lilun-shijian", "zh", "formulaic-frame", "revise",
       r"(具有|兼具)(重要的)?理論(意義|價值)和實踐(意義|價值)|(具有|兼具)(重要的)?理论(意义|价值)和实践(意义|价值)",
       "分別說出理論上與實務上的具體貢獻"),
    # stock summaries
    _p("zh-sum-zongshang", "zh", "stock-summary", "watch",
       r"綜上所述|综上所述|總而言之|总而言之|總的來說|总的来说|由此可見|由此可见", "段落結論若只是重述就刪去"),
    # hedge stacks
    _p("zh-hedge-stack", "zh", "hedge-stack", "revise",
       r"(可能|或許|或许|也許|也许)[^。，,]{0,6}(可能|或許|或许|也許|也许)", "保留一個限定詞，依證據強度選擇"),
    _p("zh-hedge-yiding", "zh", "hedge-stack", "watch", r"在一定程度上", "說出到什麼程度，或刪去"),
    # contrast templates
    _p("zh-contrast-bujin", "zh", "contrast-template", "watch",
       r"不僅[^。；;]{1,60}(而且|更|還|也)|不仅[^。；;]{1,60}(而且|更|还|也)", "偶一為之可以；反覆出現就是套路"),
    _p("zh-contrast-bushi", "zh", "contrast-template", "watch", r"不是[^。；;]{1,40}，?而是", "直接陳述正面主張"),
    # nominalization
    _p("zh-nominal-jinxing", "zh", "nominalization", "revise",
       r"(進行|进行)(了)?(深入的|系統的|系统的|全面的)?(分析|研究|探討|探讨|調查|调查|比較|比较|評估|评估|討論|讨论|檢驗|检验)",
       "去掉「進行」，直接用動詞"),
    # 防禦性寫作（references/defensive-writing.md）
    _p("zh-def-mouzhong", "zh", "defensive-hedge", "revise",
       r"某種(程度|意義)上|某种(程度|意义)上|從某種(角度|意義)(來看|上說|而言)|从某种(角度|意义)(来看|上说|而言)",
       "說出在哪種意義、到什麼程度，否則刪去"),
    _p("zh-def-huoke", "zh", "defensive-hedge", "revise",
       r"或可(認為|认为|說|说|視為|视为)|(似乎|好像)(可能|或許|或许|也許|也许)|可能(似乎|好像)"
       r"|也許可以(說|認為)|或许可以(说|认为)|似乎(可以|能夠|能够)(說|说|認為|认为)",
       "保留一個限定，依證據強度選擇，或直接陳述"),
    _p("zh-def-shuangfou", "zh", "defensive-hedge", "watch",
       r"不能(說|说)(完全)?(沒有|没有|不)|不無|不无|並非(完全)?(沒有|不)|并非(完全)?(没有|不)",
       "雙重否定是在閃躲；正面說出程度"),
    _p("zh-cav-buzu", "zh", "preemptive-caveat", "revise",
       r"(本文|本研究|研究)(也|仍|還|还|尚)?(存在|有)(一定的|一些|諸多|诸多|若干|許多|许多)?(不足|局限|侷限|缺陷)",
       "具體說出哪個限制、影響哪個結論；在研究限制一節說一次"),
    _p("zh-cav-jinshen", "zh", "preemptive-caveat", "revise",
       r"(結果|结果|結論|结论|發現|发现)(應|应|需|須|须|要)?(謹慎|谨慎|審慎|审慎)(地)?(看待|解讀|解读|解釋|解释|推論|推论|推廣|推广)",
       "說出哪個結果、為什麼、哪種解讀仍然成立"),
    _p("zh-cav-youdai", "zh", "preemptive-caveat", "revise",
       r"有待(進一步|进一步|後續|后续|未來|未来)?的?(研究|探討|探讨|驗證|验证|深入)|(仍|尚)?需(要)?(進一步|进一步)(的)?(研究|探討|探讨|驗證|验证)",
       "說出需要什麼資料或研究設計才能回答，否則刪去"),
    _p("zh-cav-dangran", "zh", "preemptive-caveat", "watch",
       r"(^|[。！？])\s*(當然|当然|誠然|诚然|固然|不過|不过)[，,]",
       "讀者不會提出的反駁，就不必先讓步"),
    _p("zh-cav-bingbushi", "zh", "preemptive-caveat", "watch",
       r"(這|这)(並|并)不(是說|是说|意味著|意味着|代表)",
       "只在讀者真的會這樣誤讀時保留"),
    _p("zh-disc-wuyi", "zh", "disclaimer", "revise",
       r"本(文|研究)(並|并)?(無意|无意|不打算|不試圖|不试图|不企圖|不企图|不求)|(無意|无意)(於|于)?(窮盡|穷尽|面面俱到)",
       "正面說明涵蓋範圍：哪些材料、哪段時間、哪些問題"),
    _p("zh-disc-pianfu", "zh", "disclaimer", "revise",
       r"(限於|限于|囿於|囿于|受限於|受限于)篇幅|篇幅(所限|有限)",
       "直接說涵蓋什麼；篇幅不是學術理由"),
    _p("zh-disc-fanwei", "zh", "disclaimer", "watch",
       r"不在本(文|研究)(的)?(討論|讨论|研究)?(範圍|范围)|超出(了)?本(文|研究)(的)?(討論|讨论|研究)?(範圍|范围)",
       "說一次可以；反覆出現就像在築圍牆"),
    _p("zh-apol-paozhuan", "zh", "apologetic-framing", "revise",
       r"拋磚引玉|抛砖引玉|不揣(淺陋|浅陋|冒昧)|才疏學淺|才疏学浅|管窺之見|管窥之见|一孔之見|一孔之见|淺見|浅见|拙見|拙见|淺陋|浅陋",
       "刪去自謙；貢獻照實說"),
    _p("zh-apol-zhizheng", "zh", "apologetic-framing", "revise",
       r"(不當|不当|不妥|疏漏|錯漏|错漏|謬誤|谬误|不足)之處(在所難免|在所难免)|(不當|不妥|疏漏)之处在所难免"
       r"|(敬請|敬请|懇請|恳请|還請|还请)[^。]{0,8}(指正|斧正|批評|批评)|(筆者|笔者)(學識|学识|水平|能力)(有限|所限)",
       "刪去；正文不向讀者道歉"),
    _p("zh-apol-changshi", "zh", "apologetic-framing", "watch",
       r"(初步|粗淺|粗浅|膚淺|肤浅|簡單|简单)的?(嘗試|尝试|探索|探討|探讨)",
       "說出做了什麼，不必先說它粗淺"),
    _p("zh-just-yanjin", "zh", "over-justification", "revise",
       r"(為了|为了|為|为)(保證|保证|確保|确保)(研究|結果|结果|分析)?(的)?(嚴謹性|严谨性|科學性|科学性|客觀性|客观性|可靠性|準確性|准确性)"
       r"|(為|为)(嚴謹|严谨|慎重|穩妥|稳妥)起見|出於(嚴謹|严谨|謹慎|谨慎)",
       "說出這一步做什麼；標準程序附引用即可，不必辯護"),
    _p("zh-just-youliyou", "zh", "over-justification", "revise",
       r"有理由(認為|认为|相信|推斷|推断)|(可以|足以)合理地?(認為|认为|推斷|推断)|不難(看出|發現|理解)|不难(看出|发现|理解)",
       "說出理由本身，或直接陳述"),
    _p("zh-just-gongren", "zh", "over-justification", "revise",
       r"(學界|学界|學術界|学术界)(普遍|一致|公認|公认)(認為|认为|認同|认同)|(公認|公认)的是",
       "附上文獻讓文獻說話；不要訴諸共識"),
]

# Shorthand for the languages below: residue, connective, emphasis,
# vocabulary, frame, summary, hedge, contrast, nominalization.
def _lang(lang, rows):
    return [_p("%s-%s" % (lang, pid), lang, cat, sev, rx, hint) for pid, cat, sev, rx, hint in rows]


JA_PATTERNS = _lang("ja", [
    ("residue-certainly", "chat-residue", "remove", r"^\s*(もちろんです|承知しました|かしこまりました)[！!。、]", "削除"),
    ("residue-here-is", "chat-residue", "remove", r"以下は.{0,6}(修正|推敲|改善|添削)(した|後の)", "削除"),
    ("residue-hope", "chat-residue", "remove", r"お役に立て(れば|たら)(幸いです|嬉しいです)", "削除"),
    ("residue-as-ai", "chat-residue", "remove", r"AI(言語モデル)?として", "削除"),
    ("conn-sarani", "stock-connective", "watch", r"(^|。)\s*(さらに|加えて)、", "論理関係を明示するか削除"),
    ("emph-yakuwari", "empty-emphasis", "revise", r"(重要な|重大な|決定的な|中心的な)役割を(果たし|担っ)", "何をどう担うのかを書く"),
    ("emph-chumoku", "empty-emphasis", "revise", r"(注目|特筆)すべき(は|点は|ことに)", "枠を外して要点を直接書く"),
    ("emph-iumademo", "empty-emphasis", "revise", r"言うまでもなく|周知のとおり|周知の通り", "根拠を示すか削除"),
    ("frame-kinnen", "formulaic-frame", "revise", r"近年.{0,25}(急速な|著しい|目覚ましい)(発展|進歩|普及)に(伴い|より|よって)", "具体的な問題から書き始める"),
    ("frame-shiten", "formulaic-frame", "revise", r"新たな(視点|知見|示唆|洞察)を(提供|与え|もたら)", "得られた知見そのものを書く"),
    ("frame-mokuteki", "formulaic-frame", "watch", r"本(研究|稿|論文)の目的は", "「本稿は〜を示す／論じる」"),
    ("sum-matome", "stock-summary", "watch", r"以上のことから|総じて|まとめると|結論として", "段落末の要約は削除"),
    ("hedge-stack", "hedge-stack", "revise", r"かもしれない可能性|可能性が(ある|あり)かもしれ|おそらく.{0,10}かもしれない", "限定は一つに"),
    ("contrast-dakede", "contrast-template", "watch", r"だけでなく.{1,40}も", "繰り返すなら直接述べる"),
    ("nominal-okonau", "nominalization", "revise", r"(分析|検討|調査|考察|比較|評価)を(行う|行った|行って|実施し)", "「分析した」など動詞で"),
    ("def-ieru", "defensive-hedge", "revise", r"と言えなくもない|と言えるのではないだろうか|と(も)?言えるかもしれない|ある意味で(は)?|ではないかと(思われる|考えられる)", "限定は一つにして言い切る"),
    ("cav-genkai", "preemptive-caveat", "revise", r"本(研究|稿)には(いくつかの|一定の)?(限界|課題)が(ある|あり)|慎重に(解釈|検討)する必要がある|さらなる(研究|検討)が(必要|求められる)|今後の課題としたい", "どの限界がどの結論に効くかを一度だけ"),
    ("disc-moura", "disclaimer", "revise", r"網羅的なものではない|網羅(すること)?を(目指す|意図する)ものではない|紙幅の(都合|関係)(上)?", "扱う範囲を肯定的に述べる"),
    ("apol-sengaku", "apologetic-framing", "revise", r"浅学非才|筆者の力不足|ご(批判|叱正|教示)を(仰ぎ|請い)たい|拙(稿|論)", "削除し、貢献をそのまま述べる"),
    ("just-datou", "over-justification", "revise", r"(妥当|合理的)であると(考えられる|言える)|厳密(性)?を期(す|する)ため", "理由そのものを書く"),
])

KO_PATTERNS = _lang("ko", [
    ("residue-certainly", "chat-residue", "remove", r"^\s*(물론입니다|알겠습니다|네,)", "삭제"),
    ("residue-here-is", "chat-residue", "remove", r"다음은 .{0,8}(수정|다듬은|개선된|교정된)", "삭제"),
    ("residue-hope", "chat-residue", "remove", r"도움이 되(었으면|길) (좋겠습니다|바랍니다)", "삭제"),
    ("residue-as-ai", "chat-residue", "remove", r"AI(로서| 언어 모델로서)", "삭제"),
    ("conn-ttohan", "stock-connective", "watch", r"(^|\. )\s*(또한|더불어|아울러),?", "실제 논리 관계를 쓰거나 삭제"),
    ("emph-yeokhal", "empty-emphasis", "revise", r"(중요한|핵심적인|결정적인|중추적인) 역할을 (한다|합니다|하고|하며|수행)", "무엇을 어떻게 하는지 쓰기"),
    ("emph-jumok", "empty-emphasis", "revise", r"주목할 (만한 |필요가 있는 )?(점은|것은)", "틀을 지우고 요점을 직접"),
    ("frame-choegeun", "formulaic-frame", "revise", r"최근 .{0,25}(급속한|빠른|급격한) (발전|변화|성장)(에 따라|으로 인해|과 함께)", "구체적 문제로 시작"),
    ("frame-sisajeom", "formulaic-frame", "revise", r"새로운 (시사점|통찰|관점|함의)을 제공", "시사점 자체를 쓰기"),
    ("frame-mokjeok", "formulaic-frame", "watch", r"본 (연구|논문)는 .{0,30}(목적으로 한다|하고자 한다)", "「본 논문은 ~을 보인다」"),
    ("sum-gyeollon", "stock-summary", "watch", r"결론적으로|요약하면|종합하면|이상을 종합하면", "단락 끝 요약은 삭제"),
    ("hedge-stack", "hedge-stack", "revise", r"가능성이 있을 수 있|아마도 .{0,12}수 있을 것", "한정어는 하나만"),
    ("contrast-ppunman", "contrast-template", "watch", r"뿐만 아니라", "반복되면 직접 진술"),
    ("nominal-jinhaeng", "nominalization", "revise", r"(분석|검토|조사|비교|평가)(을|를) (진행|수행|실시)(하였|했|한다|하였다)", "「분석하였다」처럼 동사로"),
    ("def-bolsu", "defensive-hedge", "revise", r"(라고|다고) 볼 수도 있|(라고|다고) 할 수 있을지도|어떤 의미에서(는)?|어느 정도(는)?", "한정은 하나만, 주장은 분명히"),
    ("cav-hangye", "preemptive-caveat", "revise", r"(본|이) 연구는 .{0,10}(한계|제한점)(을|를|이|가) (가지|가진|갖|있)|신중하게 해석(해야|할 필요가)|추가(적인)? 연구가 필요", "어떤 한계가 어떤 결론에 영향을 주는지 한 번만"),
    ("disc-mangna", "disclaimer", "revise", r"망라(하지|한 것은) 않|(지면|분량)(의|상) (한계|제약)|본 (연구|논문)의 범위를 (벗어나|넘어서)", "다루는 범위를 긍정문으로"),
    ("apol-bujok", "apologetic-framing", "revise", r"(부족한|미흡한) 점이 (많|있)|(질정|편달)을 (바란다|바랍니다)|졸고|미력하나마", "삭제하고 기여를 그대로 쓰기"),
    ("just-tadang", "over-justification", "revise", r"(타당|합리적)하다고 (볼 수 있|판단된)|엄밀성을 (기하기|확보하기) 위(해|하여)", "이유 자체를 쓰기"),
])

ES_PATTERNS = _lang("es", [
    ("residue-certainly", "chat-residue", "remove", r"^\s*(¡claro!|¡por supuesto!|claro,|por supuesto,)", "eliminar"),
    ("residue-here-is", "chat-residue", "remove", r"\baquí (tienes|está|te dejo) (la|el|una|un) (versión|texto|párrafo) (revisad|mejorad|corregid)", "eliminar"),
    ("residue-hope", "chat-residue", "remove", r"\bespero que (esto )?(te|le|les) (sea útil|ayude|sirva)", "eliminar"),
    ("residue-as-ai", "chat-residue", "remove", r"\bcomo (una )?(IA|inteligencia artificial|modelo de lenguaje)\b", "eliminar"),
    ("conn-ademas", "stock-connective", "watch", r"(^|\. )\s*(además|asimismo|por otro lado|adicionalmente),", "nombrar la relación o suprimir"),
    ("conn-cabe", "empty-emphasis", "revise", r"\b(cabe (destacar|señalar|mencionar|resaltar)|es (importante|fundamental|necesario) (señalar|destacar|mencionar|resaltar)) que\b", "suprimir el marco y decir el punto"),
    ("emph-papel", "empty-emphasis", "revise", r"\b(desempeña|desempeñan|juega|juegan) un papel (crucial|fundamental|clave|esencial|primordial|vital|central)\b", "decir qué hace y cómo"),
    ("vocab-adentrarse", "inflated-vocabulary", "revise", r"\badentra(rse|rnos|mos|n)? en\b|\bun amplio abanico\b|\bsinergias?\b", "palabra llana"),
    ("frame-mundo", "formulaic-frame", "revise", r"\ben (el mundo|la sociedad|el contexto) (actual|de hoy|moderno|globalizado)\b|\ben la era (digital|actual)\b", "empezar por el problema concreto"),
    ("frame-luz", "formulaic-frame", "revise", r"\barroja(r|n)? (nueva )?luz sobre\b|\bsienta(n)? las bases\b|\babre(n)? nuevas vías\b", "decir qué se sabe ahora"),
    ("frame-objetivo", "formulaic-frame", "watch", r"\bel presente (estudio|trabajo|artículo) (tiene como objetivo|pretende|busca)\b", "«Este artículo sostiene / estima»"),
    ("sum-conclusion", "stock-summary", "watch", r"(^|\. )\s*(en conclusión|en resumen|en definitiva|en suma),", "el título ya lo dice"),
    ("hedge-stack", "hedge-stack", "revise", r"\b(podría|puede|podrían|pueden) (posiblemente|potencialmente|quizás)\b|\bquizás (podría|pueda)\b", "una sola matización"),
    ("contrast-nosolo", "contrast-template", "watch", r"\bno solo\b[^.;]{1,120}\bsino (también|que)\b", "afirmar directamente si se repite"),
    ("nominal-llevar", "nominalization", "watch", r"\b(llevar a cabo|realizar|efectuar) (un|una) (análisis|estudio|evaluación|revisión)\b", "usar el verbo"),
    ("def-podria-decirse", "defensive-hedge", "revise", r"\b(podría|cabría|se podría) (decirse|afirmarse|argumentarse|sostenerse)\b|\ben cierto (sentido|modo)\b|\bde alguna manera\b", "una sola matización; afirmar o atribuir"),
    ("cav-limitaciones", "preemptive-caveat", "revise", r"\b(si bien|aunque) (este|el presente) (estudio|trabajo|artículo) (tiene|presenta) (algunas |ciertas )?limitaciones\b|\b(los|estos) resultados deben (interpretarse|tomarse) con (cautela|precaución)\b|\bse (requiere|requieren|necesita|necesitan) (más|futuras|nuevas) investigaciones\b", "decir qué limitación afecta a qué resultado, una vez"),
    ("disc-exhaustivo", "disclaimer", "revise", r"\bno (pretende|aspira a) ser (exhaustiv|definitiv|complet)\w*|\bexcede el alcance de (este|el presente)\b", "decir el alcance real en positivo"),
    ("apol-modesta", "apologetic-framing", "revise", r"\b(modesta|humilde) (contribución|aportación)\b|\bhumildemente\b|\bmodesto (intento|aporte)\b", "decir qué aporta, sin disculparse"),
    ("just-razonable", "over-justification", "revise", r"\bes (razonable|lícito|legítimo) (suponer|pensar|afirmar|concluir)\b|\ben aras del rigor\b|\bcon el fin de garantizar el rigor\b", "dar la razón misma"),
])

FR_PATTERNS = _lang("fr", [
    ("residue-certainly", "chat-residue", "remove", r"^\s*(bien sûr|certainement|absolument)\s?[!,.]", "supprimer"),
    ("residue-here-is", "chat-residue", "remove", r"\bvoici (la|le|une|un) (version|texte|paragraphe) (révisé|amélioré|corrigé)", "supprimer"),
    ("residue-hope", "chat-residue", "remove", r"\bj'espère que (cela|ceci) (vous|t')(aide|sera utile)", "supprimer"),
    ("residue-as-ai", "chat-residue", "remove", r"\ben tant qu'(IA|intelligence artificielle|modèle de langage)\b", "supprimer"),
    ("conn-deplus", "stock-connective", "watch", r"(^|\. )\s*(de plus|en outre|par ailleurs|qui plus est),", "nommer la relation ou supprimer"),
    ("emph-convient", "empty-emphasis", "revise", r"\bil (est important|convient|est essentiel|faut) de (noter|souligner|rappeler|mentionner) que\b", "supprimer le cadre"),
    ("emph-role", "empty-emphasis", "revise", r"\bjoue(nt)? un rôle (crucial|clé|essentiel|primordial|fondamental|majeur|central|déterminant)\b", "dire ce qu'il fait et comment"),
    ("vocab-paysage", "inflated-vocabulary", "watch", r"\bpaysage (complexe|en constante évolution)\b|\bsynergies?\b|\bplonger dans\b", "mot simple"),
    ("frame-monde", "formulaic-frame", "revise", r"\bdans (le monde|la société|le contexte) (actuel|actuelle|d'aujourd'hui|moderne|globalisé)\b|\bà l'ère (du numérique|numérique|actuelle)\b", "commencer par le problème précis"),
    ("frame-lumiere", "formulaic-frame", "revise", r"\b(met|mettent) en lumière\b|\bouvre(nt)? (la voie|de nouvelles perspectives)\b|\bapporte(nt)? un éclairage nouveau\b", "dire ce qu'on sait désormais"),
    ("frame-vise", "formulaic-frame", "watch", r"\b(cette|la présente) (étude|recherche|contribution) vise à\b|\bcet article vise à\b", "« Cet article montre / soutient »"),
    ("sum-conclusion", "stock-summary", "watch", r"(^|\. )\s*(en conclusion|en résumé|en somme|pour conclure),", "le titre le dit déjà"),
    ("hedge-stack", "hedge-stack", "revise", r"\bpourrai(t|ent) (éventuellement|potentiellement|peut-être)\b|\bpeut-être pourrai(t|ent)\b", "une seule nuance"),
    ("contrast-nonseulement", "contrast-template", "watch", r"\bnon seulement\b[^.;]{1,120}\bmais (aussi|également|encore)\b", "affirmer directement si répété"),
    ("nominal-proceder", "nominalization", "watch", r"\b(procéder à|effectuer|réaliser) (une|un) (analyse|étude|évaluation|examen)\b", "utiliser le verbe"),
    ("def-pourrait-dire", "defensive-hedge", "revise", r"\b(on|l'on) pourrait (dire|avancer|soutenir|affirmer)\b|\bdans une certaine mesure\b|\bd'une certaine (manière|façon)\b|\ben quelque sorte\b", "une seule nuance ; assumer ou attribuer"),
    ("cav-limites", "preemptive-caveat", "revise", r"\b(bien que|même si) (cette|la présente) (étude|recherche) (présente|comporte|ait) (certaines |quelques )?limites\b|\b(ces |les )?résultats doivent être (interprétés|pris) avec (prudence|précaution)\b|\bdes recherches (futures|ultérieures|supplémentaires) sont nécessaires\b", "dire quelle limite touche quel résultat, une fois"),
    ("disc-exhaustif", "disclaimer", "revise", r"\bne (prétend|vise) pas à (l')?(être )?(exhausti|définiti|complet)\w*|\bsans prétendre à l'exhaustivité\b|\bdépasse le cadre de (cet|cette|la présente)\b", "dire la portée réelle en positif"),
    ("apol-modeste", "apologetic-framing", "revise", r"\b(modeste|humble) (contribution|tentative|essai)\b|\bhumblement\b|\bnous nous permettons de\b", "dire ce que le travail apporte"),
    ("just-raisonnable", "over-justification", "revise", r"\bil (est|semble) (raisonnable|légitime|permis) de (supposer|penser|conclure|considérer)\b|\bpar souci de rigueur\b|\bafin de garantir la rigueur\b", "donner la raison elle-même"),
])

DE_PATTERNS = _lang("de", [
    ("residue-certainly", "chat-residue", "remove", r"^\s*(natürlich|gerne|selbstverständlich)\s?[!,.]", "streichen"),
    ("residue-here-is", "chat-residue", "remove", r"\bhier ist (die|der|eine|ein) (überarbeitete|verbesserte|korrigierte|polierte)", "streichen"),
    ("residue-hope", "chat-residue", "remove", r"\bich hoffe,? (das|dies) hilft\b", "streichen"),
    ("residue-as-ai", "chat-residue", "remove", r"\bals (KI|künstliche Intelligenz|Sprachmodell)\b", "streichen"),
    ("conn-darueber", "stock-connective", "watch", r"(^|\. )\s*(darüber hinaus|außerdem|zudem|des Weiteren|ferner)\b", "Beziehung benennen oder streichen"),
    ("emph-wichtig", "empty-emphasis", "revise", r"\b(es (ist|sei)|ist es|sei es) (wichtig|hervorzuheben|darauf hinzuweisen|anzumerken),? (zu (beachten|betonen|erwähnen),? )?dass\b", "Rahmen streichen, Punkt nennen"),
    ("emph-rolle", "empty-emphasis", "revise", r"\bspiel(t|en)(?: [\w-]+){0,4} eine (entscheidende|zentrale|wichtige|wesentliche|maßgebliche|bedeutende|tragende) Rolle\b", "sagen, was es bewirkt"),
    ("vocab-landschaft", "inflated-vocabulary", "watch", r"\b(vielschichtige|komplexe|sich wandelnde) Landschaft\b|\bSynergien?\b|\beintauchen in\b", "schlichtes Wort"),
    ("frame-heute", "formulaic-frame", "revise", r"\bin der heutigen (schnelllebigen |digitalen |globalisierten )?(Welt|Zeit|Gesellschaft)\b|\bim Zeitalter der Digitalisierung\b", "mit dem konkreten Problem beginnen"),
    ("frame-licht", "formulaic-frame", "revise", r"\bwirf(t|en) (ein )?(neues )?Licht auf\b|\bebne(t|n) den Weg\b|\beröffne(t|n) neue (Perspektiven|Wege)\b", "sagen, was jetzt bekannt ist"),
    ("frame-ziel", "formulaic-frame", "watch", r"\bZiel (dieser|der vorliegenden) (Arbeit|Studie|Untersuchung) ist es\b", "„Dieser Beitrag zeigt / argumentiert“"),
    ("sum-zusammenfassend", "stock-summary", "watch", r"\bzusammenfassend (lässt sich (sagen|festhalten)|ist festzuhalten)\b|\babschließend lässt sich\b", "Überschrift sagt es schon"),
    ("hedge-stack", "hedge-stack", "revise", r"\bkönnte(n)? (möglicherweise|eventuell|potenziell|vielleicht)\b", "nur eine Einschränkung"),
    ("contrast-nichtnur", "contrast-template", "watch", r"\bnicht nur\b[^.;]{1,120}\bsondern auch\b", "bei Wiederholung direkt sagen"),
    ("nominal-durchgefuehrt", "nominalization", "watch", r"\b(Analyse|Untersuchung|Bewertung|Überprüfung|Auswertung) (wurde |wird |werden )?durchgeführt\b", "Verb verwenden"),
    ("def-koennte-sagen", "defensive-hedge", "revise", r"\b(man )?könnte (man )?(sagen|argumentieren|behaupten)\b|\bin gewisser (Weise|Hinsicht)\b|\bgewissermaßen\b|\bin gewissem (Maße|Umfang)\b", "eine Einschränkung; behaupten oder belegen"),
    ("cav-grenzen", "preemptive-caveat", "revise", r"\b(obwohl|auch wenn) (diese|die vorliegende) (Studie|Arbeit|Untersuchung) (gewisse |einige )?(Grenzen|Limitationen|Einschränkungen) (hat|aufweist)\b|\bErgebnisse (sind|sollten) (nur )?mit Vorsicht (zu )?interpretier\w*|\bweitere Forschung ist (nötig|notwendig|erforderlich)\b", "sagen, welche Grenze welches Ergebnis betrifft, einmal"),
    ("disc-vollstaendig", "disclaimer", "revise", r"\bkeinen Anspruch auf (Vollständigkeit|Allgemeingültigkeit)\b|\bden Rahmen (dieser|der vorliegenden) (Arbeit|Studie|Untersuchung) sprengen\b|\bsprengt den Rahmen\b", "den tatsächlichen Umfang positiv nennen"),
    ("apol-bescheiden", "apologetic-framing", "revise", r"\b(bescheidene[nr]?|kleine[nr]?) (Beitrag|Versuch)\b|\bin aller Bescheidenheit\b", "sagen, was die Arbeit beiträgt"),
    ("just-vernuenftig", "over-justification", "revise", r"\bes (ist|scheint) (daher |somit )?(vernünftig|plausibel|legitim|gerechtfertigt),? anzunehmen\b|\bder Vollständigkeit halber\b|\bum (die )?(Wissenschaftlichkeit|Objektivität|Validität) zu (gewährleisten|sichern)\b", "den Grund selbst nennen"),
])

PT_PATTERNS = _lang("pt", [
    ("residue-certainly", "chat-residue", "remove", r"^\s*(claro!|com certeza!|claro,|com certeza,)", "eliminar"),
    ("residue-here-is", "chat-residue", "remove", r"\baqui está (a|o|uma|um) (versão|texto|parágrafo) (revisad|melhorad|corrigid)", "eliminar"),
    ("residue-hope", "chat-residue", "remove", r"\bespero que (isso|isto) (ajude|seja útil)\b", "eliminar"),
    ("residue-as-ai", "chat-residue", "remove", r"\bcomo (uma )?(IA|inteligência artificial|modelo de linguagem)\b", "eliminar"),
    ("conn-alem", "stock-connective", "watch", r"(^|\. )\s*(além disso|ademais|adicionalmente|outrossim),", "nomear a relação ou suprimir"),
    ("emph-vale", "empty-emphasis", "revise", r"\b(é (importante|fundamental|necessário)|vale) (ressaltar|destacar|notar|salientar|mencionar) que\b", "suprimir o enquadramento"),
    ("emph-papel", "empty-emphasis", "revise", r"\b(desempenha|desempenham) um papel (crucial|fundamental|essencial|chave|primordial|central|vital)\b", "dizer o que faz e como"),
    ("vocab-cenario", "inflated-vocabulary", "watch", r"\bcenário (complexo|em constante evolução)\b|\bsinergias?\b|\bmergulhar em\b", "palavra simples"),
    ("frame-mundo", "formulaic-frame", "revise", r"\bno (mundo|cenário|contexto) (atual|contemporâneo|de hoje|globalizado)\b|\bna era (digital|atual)\b", "começar pelo problema concreto"),
    ("frame-luz", "formulaic-frame", "revise", r"\blança(m)? (nova )?luz sobre\b|\babre(m)? (caminho|novas perspectivas)\b", "dizer o que se sabe agora"),
    ("frame-objetivo", "formulaic-frame", "watch", r"\bo presente (estudo|trabalho|artigo) (tem como objetivo|visa|busca)\b", "«Este artigo mostra / argumenta»"),
    ("sum-conclusao", "stock-summary", "watch", r"(^|\. )\s*(em conclusão|em suma|em resumo|em síntese),", "o título já diz"),
    ("hedge-stack", "hedge-stack", "revise", r"\b(poderia|pode|poderiam|podem) (possivelmente|potencialmente|talvez)\b|\btalvez (possa|poderia)\b", "uma só ressalva"),
    ("contrast-naoso", "contrast-template", "watch", r"\bnão (só|apenas|somente)\b[^.;]{1,120}\bmas também\b", "afirmar diretamente se repetido"),
    ("nominal-realizar", "nominalization", "watch", r"\b(realizar|efetuar|conduzir) (uma|um) (análise|estudo|avaliação|revisão)\b", "usar o verbo"),
    ("def-poderia-dizer", "defensive-hedge", "revise", r"\b(poderia|pode)-se (dizer|argumentar|afirmar)\b|\bde certa (forma|maneira)\b|\bem certo sentido\b|\bem certa medida\b", "uma só ressalva; afirmar ou atribuir"),
    ("cav-limitacoes", "preemptive-caveat", "revise", r"\b(embora|ainda que) (este|o presente) (estudo|trabalho|artigo) (tenha|apresente) (algumas |certas )?limitações\b|\b(os |estes )?resultados devem ser interpretados com (cautela|cuidado)\b|\b(são necessárias|é necessária) (mais|novas|futuras) pesquisas?\b", "dizer que limitação afeta que resultado, uma vez"),
    ("disc-exaustivo", "disclaimer", "revise", r"\bnão (pretende|tem a pretensão de) ser (exaustiv|definitiv|complet)\w*|\bfoge ao escopo (deste|do presente)\b|\bextrapola o escopo\b", "dizer o escopo real em positivo"),
    ("apol-modesta", "apologetic-framing", "revise", r"\b(modesta|humilde) (contribuição|tentativa)\b|\bhumildemente\b", "dizer o que o trabalho traz"),
    ("just-razoavel", "over-justification", "revise", r"\bé (razoável|lícito|legítimo) (supor|pensar|afirmar|concluir)\b|\bem nome do rigor\b|\ba fim de garantir o rigor\b", "dar a própria razão"),
])

RU_PATTERNS = _lang("ru", [
    ("residue-certainly", "chat-residue", "remove", r"^\s*(конечно|разумеется)\s?[!,.]", "удалить"),
    ("residue-here-is", "chat-residue", "remove", r"(?<![\w-])вот (исправленн|отредактированн|улучшенн|переработанн)\w* (вариант|текст|версия)", "удалить"),
    ("residue-hope", "chat-residue", "remove", r"(?<![\w-])надеюсь, это (поможет|было полезно)", "удалить"),
    ("residue-as-ai", "chat-residue", "remove", r"(?<![\w-])как (ИИ|языковая модель|искусственный интеллект)(?![\w-])", "удалить"),
    ("conn-krome", "stock-connective", "watch", r"(^|\. )\s*(кроме того|более того|помимо этого|вместе с тем),", "назвать связь или убрать"),
    ("emph-vazhno", "empty-emphasis", "revise", r"(?<![\w-])(важно|следует|стоит|необходимо) (отметить|подчеркнуть|указать),? что", "убрать рамку и сказать суть"),
    ("emph-rol", "empty-emphasis", "revise", r"(?<![\w-])игра(ет|ют) (ключевую|важную|решающую|существенную|важнейшую|центральную) роль", "сказать, что именно делает"),
    ("vocab-landshaft", "inflated-vocabulary", "watch", r"(?<![\w-])(многогранн\w+|синерги\w+|погрузиться в)", "простое слово"),
    ("frame-mir", "formulaic-frame", "revise", r"(?<![\w-])в (современном|сегодняшнем|быстро меняющемся) (мире|обществе)|(?<![\w-])в эпоху (цифровизации|цифровых технологий)", "начать с конкретной проблемы"),
    ("frame-svet", "formulaic-frame", "revise", r"(?<![\w-])пролива(ет|ют) (новый )?свет на|(?<![\w-])открыва(ет|ют) новые (возможности|перспективы|горизонты)", "сказать, что теперь известно"),
    ("frame-cel", "formulaic-frame", "watch", r"(?<![\w-])целью (данного|настоящего) (исследования|статьи|работы) является", "«В статье показано / доказывается»"),
    ("sum-itog", "stock-summary", "watch", r"(^|\. )\s*(в заключение|подводя итог|резюмируя),", "заголовок уже это говорит"),
    ("hedge-stack", "hedge-stack", "revise", r"(?<![\w-])(может|могут) (потенциально|возможно)(?![\w-])|(?<![\w-])возможно,? (может|могут)(?![\w-])", "одна оговорка"),
    ("contrast-netolko", "contrast-template", "watch", r"(?<![\w-])не только(?![\w-])[^.;]{1,120}(?<![\w-])но и(?![\w-])", "при повторе сказать прямо"),
    ("nominal-provedenie", "nominalization", "watch", r"(?<![\w-])(провед|осуществл)\w* (анализ|исследовани|оценк)\w*", "использовать глагол"),
    ("def-mozhno-skazat", "defensive-hedge", "revise", r"(?<![\w-])(можно было бы|можно) (сказать|утверждать)(?![\w-])|(?<![\w-])в (некотором|определённом|определенном) (смысле|роде)(?![\w-])|(?<![\w-])в (какой-то|определённой|определенной) (мере|степени)(?![\w-])", "одна оговорка; утверждать или ссылаться"),
    ("cav-ogranichenia", "preemptive-caveat", "revise", r"(?<![\w-])(хотя|несмотря на то,? что) (данное|настоящее) исследование (имеет|не лишено) (ряд\w* |некоторы\w+ )?ограничени\w*|(?<![\w-])результаты следует (интерпретировать|трактовать) с осторожностью|(?<![\w-])требуются дальнейшие исследования", "сказать, какое ограничение влияет на какой вывод, один раз"),
    ("disc-polnota", "disclaimer", "revise", r"(?<![\w-])не претенду\w+ на (полноту|исчерпывающ\w+|окончательн\w+)|(?<![\w-])выходит за рамки (данной|настоящей|этой) (статьи|работы)", "назвать реальный охват"),
    ("apol-skromny", "apologetic-framing", "revise", r"(?<![\w-])скромн\w+ (вклад|попытк\w+)(?![\w-])", "сказать, что работа даёт"),
    ("just-razumno", "over-justification", "revise", r"(?<![\w-])(представляется|является) (разумным|обоснованным|правомерным) (предположить|считать|утверждать)(?![\w-])|(?<![\w-])(для|ради) (полноты|строгости)(?![\w-])", "назвать саму причину"),
])

CATALOG = {
    "en": EN_PATTERNS, "zh": ZH_PATTERNS, "ja": JA_PATTERNS, "ko": KO_PATTERNS, "es": ES_PATTERNS,
    "fr": FR_PATTERNS, "de": DE_PATTERNS, "pt": PT_PATTERNS, "ru": RU_PATTERNS,
}
ALL_PATTERNS: List[Pattern] = [p for rows in CATALOG.values() for p in rows]


def patterns_for(lang: str) -> List[Pattern]:
    """The phrase catalog for ``lang``; empty for a language without one
    (structural checks and protected-item checks still apply)."""
    return list(CATALOG.get(lang, []))
