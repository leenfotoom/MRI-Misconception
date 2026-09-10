from __future__ import annotations

from typing import Any

from .ai.misconception_classifier import lexical_scores
from .ai.reasoning_parser import parse_reasoning


PRACTICE_BY_SCENARIO: dict[str, dict[str, Any]] = {
    "S1": {
        "question": "Two identical lamps exchange labels but remain in the same series loop. Which lamp is brighter?",
        "question_ar": "تم تبديل اسمي مصباحين متطابقين وبقيا في دائرة التوالي نفسها. أيهما أكثر سطوعًا؟",
        "options": [("A", "Lamp A", "المصباح A"), ("B", "Lamp B", "المصباح B"), ("same", "Same brightness", "نفس السطوع")],
        "correct_answer": "same",
        "correct_model": "In one ideal series loop, the same current passes through every component. Identical lamps therefore dissipate equal power, independent of drawing position or label.",
        "correct_model_ar": "في حلقة توالٍ مثالية يمر التيار نفسه في كل مكوّن. لذلك تبدد المصابيح المتطابقة قدرة متساوية بغض النظر عن موقع الرسم أو الاسم.",
        "lesson": ["Trace one closed loop, not a first-to-last delivery path.", "Use equal series current.", "Compare power only after current and resistance are known."],
        "lesson_ar": ["تتبّع حلقة مغلقة واحدة، لا مسار توصيل من الأول إلى الأخير.", "استخدم حقيقة تساوي تيار التوالي.", "قارن القدرة بعد معرفة التيار والمقاومة."],
        "resolved_signals": ["same current", "equal current", "equal power", "identical", "series loop", "نفس التيار", "تيار متساو", "قدرة متساوية", "متطابق", "توالي"],
        "persistent_signals": ["closer", "first", "reaches before", "uses current", "near battery", "أقرب", "أول", "تصل قبل", "يستهلك التيار"],
    },
    "S2": {
        "question": "A 9 V source drives 10Ω, then the total series resistance becomes 20Ω. What happens to total current?",
        "question_ar": "مصدر 9V يغذي مقاومة 10Ω ثم أصبحت مقاومة التوالي الكلية 20Ω. ماذا يحدث للتيار الكلي؟",
        "options": [("A", "It decreases", "ينخفض"), ("B", "It increases", "يرتفع"), ("same", "It stays the same", "يبقى نفسه")],
        "correct_answer": "A",
        "correct_model": "For a fixed voltage source, total current is I = V/R. Increasing total series resistance decreases the current drawn from the source.",
        "correct_model_ar": "عند ثبات الجهد يكون التيار الكلي I = V/R. زيادة مقاومة التوالي الكلية تقلل التيار المسحوب من المصدر.",
        "lesson": ["Hold source voltage constant.", "Add series resistances.", "Apply I = V/R to the whole loop."],
        "lesson_ar": ["ثبّت جهد المصدر.", "اجمع مقاومات التوالي.", "طبّق I = V/R على الحلقة كاملة."],
        "resolved_signals": ["I = V/R", "ohm", "resistance increases", "current decreases", "inverse", "قانون أوم", "المقاومة تزيد", "التيار يقل", "علاقة عكسية"],
        "persistent_signals": ["fixed current", "same current", "battery sends", "لا يتغير التيار", "تيار ثابت", "البطارية ترسل"],
    },
    "S3": {
        "question": "Two parallel branches are 12Ω and 24Ω across the same voltage. Which branch carries more current?",
        "question_ar": "فرعان متوازيان 12Ω و24Ω تحت الجهد نفسه. أي فرع يحمل تيارًا أكبر؟",
        "options": [("A", "12Ω branch", "فرع 12Ω"), ("B", "24Ω branch", "فرع 24Ω"), ("same", "Equal current", "تيار متساوٍ")],
        "correct_answer": "A",
        "correct_model": "Parallel branches share voltage, not necessarily current. With the same voltage, the lower-resistance branch carries more current because I = V/R.",
        "correct_model_ar": "فروع التوازي تتشارك الجهد وليس بالضرورة التيار. عند الجهد نفسه يحمل الفرع الأقل مقاومة تيارًا أكبر لأن I = V/R.",
        "lesson": ["Mark the equal branch voltage.", "Calculate each branch current separately.", "Compare V/R values."],
        "lesson_ar": ["حدّد الجهد المتساوي على الفروع.", "احسب تيار كل فرع منفصلًا.", "قارن قيم V/R."],
        "resolved_signals": ["same voltage", "lower resistance", "more current", "V/R", "نفس الجهد", "مقاومة أقل", "تيار أكبر"],
        "persistent_signals": ["splits equally", "equal current", "parallel means equal", "ينقسم بالتساوي", "تيار متساو"],
    },
    "S4": {
        "question": "Ideal ammeters are placed at two different points in one unbranched series loop. How do their readings compare?",
        "question_ar": "وُضع أميتران مثاليان في نقطتين مختلفتين من حلقة توالٍ بلا تفرعات. كيف تتقارن قراءتاهما؟",
        "options": [("A", "First is higher", "الأول أكبر"), ("B", "Second is higher", "الثاني أكبر"), ("same", "Same current", "نفس التيار")],
        "correct_answer": "same",
        "correct_model": "Charge does not accumulate in a steady unbranched loop, so the current is the same at every point. Components transfer energy; they do not consume current.",
        "correct_model_ar": "لا تتراكم الشحنة في حلقة ثابتة بلا تفرعات، لذلك يكون التيار نفسه في كل نقطة. المكونات تنقل الطاقة ولا تستهلك التيار.",
        "lesson": ["Separate current from energy.", "Check whether the path branches.", "Use current continuity in a single loop."],
        "lesson_ar": ["افصل بين التيار والطاقة.", "تحقق هل يوجد تفرع في المسار.", "استخدم استمرارية التيار في الحلقة الواحدة."],
        "resolved_signals": ["same current", "continuity", "no branch", "energy not current", "نفس التيار", "استمرارية", "لا يوجد تفرع", "الطاقة وليس التيار"],
        "persistent_signals": ["used up", "consumed", "less reaches", "first higher", "يستهلك", "تيار أقل", "الأول أكبر"],
    },
    "T1": {
        "question": "After a = 7, b = a, then a = 9, what value is stored in b?",
        "question_ar": "بعد a = 7 ثم b = a ثم a = 9، ما القيمة المخزنة في b؟",
        "options": [("A", "7", "7"), ("B", "9", "9"), ("same", "Error", "خطأ")],
        "correct_answer": "A",
        "correct_model": "A normal assignment copies the value that exists at that moment. Reassigning a later does not rewrite the value already stored in b.",
        "correct_model_ar": "الإسناد العادي ينسخ القيمة الموجودة في تلك اللحظة. إعادة إسناد a لاحقًا لا تعيد كتابة القيمة المخزنة مسبقًا في b.",
        "lesson": ["Execute one line at a time.", "Write the state after every assignment.", "Distinguish copying a value from a live reference."],
        "lesson_ar": ["نفّذ سطرًا واحدًا كل مرة.", "اكتب الحالة بعد كل إسناد.", "ميّز نسخ القيمة عن المرجع الحي."],
        "resolved_signals": ["copies", "snapshot", "value at that time", "line by line", "نسخ", "لحظة الإسناد", "سطر بسطر"],
        "persistent_signals": ["tracks", "linked", "changes with", "final value", "مرتبطة", "تتغير مع", "القيمة النهائية"],
    },
    "T2": {
        "question": "How many values are produced by range(2, 6)?",
        "question_ar": "كم قيمة تنتج range(2, 6)؟",
        "options": [("A", "4 values", "4 قيم"), ("B", "5 values", "5 قيم"), ("same", "Infinite", "لا نهائي")],
        "correct_answer": "A",
        "correct_model": "Python range is half-open: it includes the start and excludes the stop. range(2, 6) produces 2, 3, 4, and 5.",
        "correct_model_ar": "range في Python نصف مفتوحة: تشمل البداية وتستبعد stop. لذلك range(2, 6) تنتج 2 و3 و4 و5.",
        "lesson": ["List produced values before counting.", "Include start.", "Exclude stop."],
        "lesson_ar": ["اكتب القيم الناتجة قبل العد.", "اشمل البداية.", "استبعد stop."],
        "resolved_signals": ["stop excluded", "excludes 6", "half-open", "2 3 4 5", "يستبعد", "لا تشمل 6", "نصف مفتوحة"],
        "persistent_signals": ["includes 6", "stop included", "five values", "تشمل 6", "الحد الأخير", "خمس قيم"],
    },
    "T3": {
        "question": "Without parentheses, is active OR premium AND trial evaluated as active OR (premium AND trial)?",
        "question_ar": "من دون أقواس، هل يُقيّم active OR premium AND trial بالشكل active OR (premium AND trial)؟",
        "options": [("A", "Yes, equivalent", "نعم، متكافئان"), ("B", "No, left-to-right", "لا، من اليسار لليمين"), ("same", "AND and OR are identical", "AND وOR متطابقان")],
        "correct_answer": "A",
        "correct_model": "SQL evaluates AND before OR unless parentheses override precedence. Parentheses make the intended grouping explicit and safer to review.",
        "correct_model_ar": "يقيّم SQL العامل AND قبل OR ما لم تغيّر الأقواس الأولوية. الأقواس تجعل التجميع المقصود واضحًا وأسهل للمراجعة.",
        "lesson": ["Identify each Boolean operator.", "Apply AND before OR.", "Use parentheses to state intent."],
        "lesson_ar": ["حدّد كل عامل منطقي.", "طبّق AND قبل OR.", "استخدم الأقواس لتوضيح القصد."],
        "resolved_signals": ["AND before OR", "precedence", "parentheses", "AND قبل OR", "الأولوية", "الأقواس"],
        "persistent_signals": ["left to right", "same operator", "no precedence", "من اليسار", "نفس العامل", "لا أولوية"],
    },
    "T4": {
        "question": "A model gets 990 majority cases correct but detects 0 of 20 minority cases. Is overall accuracy enough to approve it?",
        "question_ar": "نموذج يصيب 990 حالة أغلبية لكنه لا يكتشف أيًا من 20 حالة أقلية. هل تكفي الدقة الكلية لاعتماده؟",
        "options": [("A", "Yes, accuracy is high", "نعم، الدقة مرتفعة"), ("B", "No, inspect minority recall", "لا، افحص استدعاء الأقلية"), ("same", "Class balance does not matter", "توازن الفئات لا يهم")],
        "correct_answer": "B",
        "correct_model": "Overall accuracy can hide total failure on a rare but important class. Evaluate the confusion matrix and per-class precision/recall before judging the model.",
        "correct_model_ar": "قد تخفي الدقة الكلية فشلًا كاملًا في فئة نادرة لكنها مهمة. يجب فحص confusion matrix وprecision/recall لكل فئة قبل الحكم على النموذج.",
        "lesson": ["Inspect class counts first.", "Read the confusion matrix by class.", "Prioritize minority recall when missing positives is costly."],
        "lesson_ar": ["افحص أعداد الفئات أولًا.", "اقرأ confusion matrix لكل فئة.", "أعطِ أولوية لاستدعاء الأقلية عندما يكون تفويت الحالات مكلفًا."],
        "resolved_signals": ["minority recall", "class imbalance", "confusion matrix", "per-class", "false negative", "استدعاء الأقلية", "عدم توازن", "مصفوفة الارتباك", "لكل فئة"],
        "persistent_signals": ["accuracy is enough", "accuracy alone is enough", "high accuracy proves", "approve it because accuracy", "الدقة تكفي", "الدقة وحدها تكفي", "الدقة العالية تثبت"],
    },
    "ENG1": {
        "question": "A point load moves closer to the right support of a simply supported beam. Which reaction becomes larger?",
        "question_ar": "اقترب حمل نقطي من المسند الأيمن لعارضة بسيطة. أي رد فعل يصبح أكبر؟",
        "options": [("A", "Left reaction", "رد الفعل الأيسر"), ("B", "Right reaction", "رد الفعل الأيمن"), ("same", "They stay equal", "يبقيان متساويين")],
        "correct_answer": "B",
        "correct_model": "Support reactions follow force and moment equilibrium. Moving a load toward one support increases that support's reaction and reduces the other.",
        "correct_model_ar": "تتبع ردود الأفعال اتزان القوى والعزوم. اقتراب الحمل من مسند يزيد رد فعله ويقلل رد فعل المسند الآخر.",
        "lesson": ["Draw the free-body diagram.", "Apply sum of vertical forces.", "Take moments about one support."],
        "lesson_ar": ["ارسم مخطط الجسم الحر.", "طبّق مجموع القوى الرأسية.", "خذ العزوم حول أحد المسندين."],
        "resolved_signals": ["moment", "equilibrium", "closer support", "lever arm", "عزم", "اتزان", "المسند الأقرب", "ذراع"],
        "persistent_signals": ["always equal", "half each", "same reaction", "متساويان دائمًا", "نصف الحمل", "نفس الرد"],
    },
    "ENG2": {
        "question": "Two bars carry the same axial force; A has half the cross-sectional area of B. Which has higher stress?",
        "question_ar": "قضيبان يحملان القوة المحورية نفسها؛ مساحة A نصف مساحة B. أيهما إجهاده أكبر؟",
        "options": [("A", "Bar A", "القضيب A"), ("B", "Bar B", "القضيب B"), ("same", "Same stress", "نفس الإجهاد")],
        "correct_answer": "A",
        "correct_model": "Axial stress is force divided by area. For the same force, the smaller cross-sectional area produces higher stress.",
        "correct_model_ar": "الإجهاد المحوري يساوي القوة مقسومة على المساحة. عند القوة نفسها تنتج المساحة الأصغر إجهادًا أكبر.",
        "lesson": ["Keep internal force separate from stress.", "Use stress = F/A.", "Compare areas after forces are known."],
        "lesson_ar": ["افصل القوة الداخلية عن الإجهاد.", "استخدم الإجهاد = F/A.", "قارن المساحات بعد معرفة القوى."],
        "resolved_signals": ["F/A", "force divided by area", "smaller area", "higher stress", "القوة على المساحة", "مساحة أصغر", "إجهاد أكبر"],
        "persistent_signals": ["larger carries more", "size means force", "same stress because force", "الأكبر يحمل", "الحجم يحدد القوة", "نفس الإجهاد"],
    },
    "ENG3": {
        "question": "Design A is strongest but exceeds the mass limit. Design B meets minimum strength and the mass limit. Which is feasible?",
        "question_ar": "التصميم A هو الأقوى لكنه يتجاوز حد الكتلة. التصميم B يحقق المقاومة الدنيا وحد الكتلة. أيهما feasible؟",
        "options": [("A", "Design A", "التصميم A"), ("B", "Design B", "التصميم B"), ("same", "Both", "كلاهما")],
        "correct_answer": "B",
        "correct_model": "A feasible design must satisfy every hard constraint. Criteria rank feasible options; extra strength cannot compensate for violating a required limit.",
        "correct_model_ar": "يجب أن يحقق التصميم feasible جميع القيود الإلزامية. تستخدم المعايير لترتيب الخيارات المقبولة، ولا تعوّض المقاومة الزائدة خرق حد مطلوب.",
        "lesson": ["List hard constraints first.", "Eliminate infeasible designs.", "Rank survivors using criteria."],
        "lesson_ar": ["اكتب القيود الإلزامية أولًا.", "استبعد التصاميم غير المقبولة.", "رتّب الباقي باستخدام المعايير."],
        "resolved_signals": ["all constraints", "feasible", "mass limit", "criteria after", "كل القيود", "مقبول", "حد الكتلة", "المعايير بعد"],
        "persistent_signals": ["strongest is best", "strength compensates", "criteria same as constraints", "الأقوى أفضل", "القوة تعوض", "المعايير والقيود نفسها"],
    },
    "ENG4": {
        "question": "With equal priorities for cost, reliability, and speed, A wins only speed while B performs well on all three. Which is the better optimum?",
        "question_ar": "عند تساوي أولوية الكلفة والموثوقية والسرعة، يتفوق A في السرعة فقط بينما B جيد في الثلاثة. أيهما optimum أفضل؟",
        "options": [("A", "Design A", "التصميم A"), ("B", "Design B", "التصميم B"), ("same", "Same score", "نفس النتيجة")],
        "correct_answer": "B",
        "correct_model": "Multi-objective optimization combines weighted performance across competing objectives. The best option is the strongest overall trade-off, not automatically the winner of one metric.",
        "correct_model_ar": "يجمع التحسين متعدد الأهداف الأداء الموزون عبر أهداف متنافسة. الخيار الأفضل هو أقوى موازنة كلية وليس الفائز تلقائيًا في مؤشر واحد.",
        "lesson": ["Define objectives and weights.", "Normalize scores before combining.", "Inspect trade-offs and constraints."],
        "lesson_ar": ["حدّد الأهداف والأوزان.", "طبّع الدرجات قبل جمعها.", "افحص الموازنات والقيود."],
        "resolved_signals": ["weighted", "trade-off", "all objectives", "combined score", "موزون", "موازنة", "كل الأهداف", "نتيجة كلية"],
        "persistent_signals": ["one metric", "fastest wins", "cheapest wins", "مؤشر واحد", "الأسرع يفوز", "الأرخص يفوز"],
    },
    "MATH1": {
        "question": "Solve 3(x - 2) = 12.",
        "question_ar": "حل 3(x - 2) = 12.",
        "options": [("A", "x = 6", "x = 6"), ("B", "x = 2", "x = 2"), ("same", "x = -6", "x = -6")],
        "correct_answer": "A",
        "correct_model": "An equation stays true only when equivalent operations are applied consistently. Divide both sides by 3, then add 2, and verify by substitution.",
        "correct_model_ar": "تبقى المعادلة صحيحة عند تطبيق عمليات متكافئة بصورة ثابتة. اقسم الطرفين على 3 ثم أضف 2 وتحقق بالتعويض.",
        "lesson": ["Preserve equality on both sides.", "Undo operations in reverse order.", "Substitute the result to verify."],
        "lesson_ar": ["حافظ على المساواة في الطرفين.", "اعكس العمليات بالترتيب العكسي.", "عوّض بالنتيجة للتحقق."],
        "resolved_signals": ["both sides", "divide by 3", "add 2", "substitute", "الطرفين", "اقسم على 3", "أضف 2", "تعويض"],
        "persistent_signals": ["move and change sign", "first term only", "نقل وتغيير الإشارة", "الحد الأول فقط"],
    },
    "MATH2": {
        "question": "The pairs are (1,4), (1,4), and (2,5). Is this relation a function?",
        "question_ar": "الأزواج هي (1,4) و(1,4) و(2,5). هل هذه العلاقة دالة؟",
        "options": [("A", "Yes", "نعم"), ("B", "No", "لا"), ("same", "Not enough information", "المعلومات غير كافية")],
        "correct_answer": "A",
        "correct_model": "A function assigns each input exactly one output. Repeating the same pair is allowed; one input paired with two different outputs is not.",
        "correct_model_ar": "تسند الدالة لكل مدخل مخرجًا واحدًا فقط. تكرار الزوج نفسه مسموح، أما ربط مدخل واحد بمخرجين مختلفين فغير مسموح.",
        "lesson": ["Group pairs by input.", "List distinct outputs for each input.", "Reject only inputs with multiple distinct outputs."],
        "lesson_ar": ["جمّع الأزواج حسب المدخل.", "اكتب المخرجات المختلفة لكل مدخل.", "ارفض فقط المدخل الذي له مخرجات مختلفة متعددة."],
        "resolved_signals": ["each input", "one output", "same pair", "distinct outputs", "كل مدخل", "مخرج واحد", "نفس الزوج", "مخرجات مختلفة"],
        "persistent_signals": ["repeated input means no", "multiple outputs allowed", "vertical line checks y", "تكرار المدخل يعني لا", "مخرجات متعددة مسموحة", "يفحص y"],
    },
    "MATH3": {
        "question": "For x = 2,4,6 and y = 5,10,15, is y proportional to x?",
        "question_ar": "عندما x = 2,4,6 وy = 5,10,15، هل y تتناسب طرديًا مع x؟",
        "options": [("A", "Yes", "نعم"), ("B", "No", "لا"), ("same", "Only increasing", "تزداد فقط")],
        "correct_answer": "A",
        "correct_model": "Direct proportionality requires one constant ratio y/x for every pair. Co-increase or a constant difference alone is not enough.",
        "correct_model_ar": "يتطلب التناسب الطردي نسبة ثابتة y/x لكل زوج. مجرد زيادة الكميتين أو ثبات الفرق لا يكفي.",
        "lesson": ["Compute y/x for every pair.", "Compare the ratios.", "Use y = kx only when k is constant."],
        "lesson_ar": ["احسب y/x لكل زوج.", "قارن النسب.", "استخدم y = kx فقط عندما تكون k ثابتة."],
        "resolved_signals": ["constant ratio", "y/x", "same ratio", "k constant", "نسبة ثابتة", "نفس النسبة", "k ثابتة"],
        "persistent_signals": ["both increase", "constant difference", "looks linear", "كلاهما يزيد", "فرق ثابت", "خطية"],
    },
    "MATH4": {
        "question": "If a number is divisible by 6, it is divisible by 3. Is the converse always true?",
        "question_ar": "إذا كان العدد يقبل القسمة على 6 فإنه يقبل القسمة على 3. هل العكس صحيح دائمًا؟",
        "options": [("A", "Yes", "نعم"), ("B", "No; 3 is a counterexample", "لا؛ العدد 3 مثال مضاد"), ("same", "One example proves it", "مثال واحد يثبته")],
        "correct_answer": "B",
        "correct_model": "A conditional statement does not automatically prove its converse. One valid counterexample is enough to disprove an always-true converse.",
        "correct_model_ar": "العبارة الشرطية لا تثبت عكسها تلقائيًا. يكفي مثال مضاد صحيح واحد لنفي أن العكس صحيح دائمًا.",
        "lesson": ["Write the original direction.", "Reverse it explicitly.", "Search for one counterexample to the converse."],
        "lesson_ar": ["اكتب الاتجاه الأصلي.", "اعكسه بوضوح.", "ابحث عن مثال مضاد واحد للعكس."],
        "resolved_signals": ["converse", "counterexample", "3 not divisible by 6", "not automatic", "العكس", "مثال مضاد", "3 لا تقبل 6", "ليس تلقائيًا"],
        "persistent_signals": ["same statement", "reverse is true", "one example proves", "نفس العبارة", "العكس صحيح", "مثال يثبت"],
    },
}


def _options(item: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"value": value, "label": label, "label_ar": label_ar}
        for value, label, label_ar in item["options"]
    ]


def build_intervention(
    *,
    scenario: dict[str, Any],
    misconception: dict[str, Any],
    probability: float,
) -> dict[str, Any]:
    item = PRACTICE_BY_SCENARIO[scenario["id"]]
    description = misconception.get("description", misconception.get("short", ""))
    return {
        "misconception": {
            "id": misconception["id"],
            "name": misconception["short"],
            "description": description,
            "probability": probability,
        },
        "simple_explanation": (
            f"Your reasoning suggests this pattern: {description} "
            "That pattern may sometimes produce a correct choice, but it will fail when the context changes."
        ),
        "simple_explanation_ar": (
            "يشير تفسيرك إلى نموذج ذهني يحتاج إلى تصحيح. قد ينتج هذا النموذج إجابة صحيحة أحيانًا، "
            "لكنه يفشل عندما يتغير السياق؛ لذلك سنختبر طريقة التفكير نفسها."
        ),
        "correct_model": item["correct_model"],
        "correct_model_ar": item["correct_model_ar"],
        "micro_lesson": item["lesson"],
        "micro_lesson_ar": item["lesson_ar"],
        "practice": {
            "question": item["question"],
            "question_ar": item["question_ar"],
            "options": _options(item),
        },
        "verification_policy": {
            "answer_only": False,
            "requires_reasoning": True,
            "resolved_rule": "Correct transfer answer + correct-model reasoning + no repeated misconception signal.",
        },
    }


def evaluate_intervention(
    *,
    scenario: dict[str, Any],
    misconception: dict[str, Any],
    answer: str,
    reasoning: str,
) -> dict[str, Any]:
    item = PRACTICE_BY_SCENARIO[scenario["id"]]
    text = reasoning.casefold()
    parsed = parse_reasoning(reasoning, answer, [misconception])
    target_claim = misconception.get("claim")
    claim_repeated = bool(target_claim and target_claim in parsed.get("claims", []))
    persistent_signal = next(
        (signal for signal in item["persistent_signals"] if signal.casefold() in text),
        None,
    )
    resolved_signal = next(
        (signal for signal in item["resolved_signals"] if signal.casefold() in text),
        None,
    )
    lexical = lexical_scores(reasoning, [misconception]).get(misconception["id"], 0.0)
    # Lexical overlap alone is weak evidence because a correct rebuttal often names
    # the misconception (for example, "accuracy hides minority failure"). A clear
    # correct-model signal therefore overrides similarity unless an explicit
    # misconception claim or persistent phrase is also present.
    same_pattern = (
        claim_repeated
        or persistent_signal is not None
        or (lexical >= 0.34 and resolved_signal is None)
    )
    answer_correct = answer == item["correct_answer"]
    reasoning_matches = resolved_signal is not None and not same_pattern
    status = "resolved" if answer_correct and reasoning_matches else "persistent"

    if same_pattern:
        probability = min(0.96, max(0.68, 0.48 + lexical))
    elif reasoning_matches:
        probability = max(0.05, min(0.24, 0.18 + lexical * 0.15))
    else:
        probability = min(0.62, max(0.38, 0.35 + lexical * 0.4))

    evidence: list[str] = []
    evidence.append("transfer_answer_correct" if answer_correct else "transfer_answer_incorrect")
    if resolved_signal:
        evidence.append(f"correct_model_signal:{resolved_signal}")
    if persistent_signal:
        evidence.append(f"repeated_pattern_signal:{persistent_signal}")
    if claim_repeated:
        evidence.append(f"repeated_claim:{target_claim}")
    if not resolved_signal:
        evidence.append("correct_model_not_expressed")

    feedback = (
        "Resolved: the new answer is correct and the explanation uses the expected mental model without repeating the original misconception."
        if status == "resolved"
        else "Persistent: the answer, explanation, or both still fail to demonstrate the expected mental model. Review the targeted lesson and reassess with a new transfer question."
    )
    feedback_ar = (
        "تم الحل: الإجابة الجديدة صحيحة والتفسير يستخدم النموذج الذهني المتوقع من دون تكرار الفكرة الخاطئة الأصلية."
        if status == "resolved"
        else "الفكرة ما زالت مستمرة: الإجابة أو التفسير أو كلاهما لا يثبت النموذج الذهني المتوقع. راجع الدرس المستهدف ثم أعد التقييم بسؤال جديد."
    )

    return {
        "status": status,
        "answer_correct": answer_correct,
        "reasoning_matches_correct_model": reasoning_matches,
        "same_misconception_detected": same_pattern,
        "post_misconception_probability": round(probability, 4),
        "reasoning_evidence": evidence,
        "parsed_reasoning": parsed,
        "feedback": feedback,
        "feedback_ar": feedback_ar,
        "expected_answer": item["correct_answer"],
    }
