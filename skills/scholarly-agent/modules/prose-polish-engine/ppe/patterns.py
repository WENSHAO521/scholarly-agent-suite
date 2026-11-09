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
