"""Analysis text for the PDF edition of the results report.

Keys are the start of each section's <h2> heading; the block is inserted at the
end of that section. OVERALL closes the document. Numbers are quoted from the
final reports (runs/final/cohort, runs/final/dense-s0, runs/final/hf_meta).
"""

SECTIONS = {
    "Training check": [
        "All five runs trained normally: losses stayed finite, fell by about 67% from initialization, and were at their lowest at the end. Memory coverage is 100% and frequent-tier facts are recalled 117–185× more often than control facts.",
        "The single red cell is learned s2's spike ratio of 1.535 at step 9,050, just over the 1.5 limit. The other runs peak at 1.41–1.48. It is one noisy training batch near the end, and s2's held-out loss and fact recall are in line with s0 and s1, so s2 is kept in the 3-seed analysis with this flag (decided with Roie).",
        "Held-out loss still fell 1.6–1.7% over the last 2,000 steps in every run, so the models are close to, but not fully at, convergence. The same is true for all five, so comparisons between them are fair.",
    ],
    "Q1": [
        "The memory layer helps at equal compute. Every PKM model beats dense on every subject, by 0.05–0.08 nats/token (average perplexity 42.0–42.4 against 45.0). The gain also holds on USPTO, a subject none of the models trained on.",
        "Learning the keys makes no difference to quality. The random-key model (3.743) falls inside the learned seeds' range (3.739–3.748) on the average and on every subject. Seed-to-seed differences between the learned models are about 0.01 nats.",
    ],
    "Q2": [
        "Fact recall depends strongly on exposure. In training wording it is about 0.88 for frequent people, 0.43 for normal, 0.04 for rare, and at chance (0.005) for never-seen controls.",
        "The memory matters most for the middle tier. Dense recalls 0.75 of frequent facts but only 0.13 of normal ones, against about 0.43 for PKM. The memory lets the model store facts it saw about 100 times, which dense mostly cannot.",
        "Recall does not carry over to new wordings: top-1 is about 0.11 for frequent people in every model, dense included. The true value still ranks well above chance (mean rank about 64 against about 105 for controls), so the model knows the association weakly but stores it tied to the sentence form. This matches the data-check note in the plan.",
        "Random keys recall slightly less than the learned seeds (0.850 against 0.871–0.892 for frequent), a small gap.",
    ],
    "U1": [
        "Almost every slot is read (99.9%), so there are no dead slots. Only 20–22% of slots are ever a token's top choice, so most slots serve as secondary contributors.",
        "Learned keys use slots slightly less evenly than random keys (KL 0.71–0.73 against 0.78 bits), but the difference is small. Neither looks collapsed.",
    ],
    "U4": [
        "Slots do carry subject information beyond the token. In every model the real value is far above all 99 shuffles (p = 0.01, the smallest possible). The excess is about 0.17 bits, roughly a quarter of the measured 0.64 bits; the rest is what the estimator gives by chance at this sample size.",
        "Learned keys are a little more subject-specific than random keys (0.165–0.184 against 0.152). Random keys still show most of the effect, though, because the queries and values learn even when the keys cannot move.",
    ],
    "E1": [
        "Removing a subject's own slots hurts that subject more than matched random slots do, in every subject and model where a control was found. So the subject-specific slots U4 finds are also used.",
        "The effect is small. Switching off 64 of 65,536 slots (0.1%) costs about 0.008 nats on average, against 0.8 nats for switching off the whole layer.",
        "It grows roughly in proportion to the number of slots removed: 0.002 at 16, 0.008 at 64, 0.034 at 256, about ×4 per ×4. There is no sign of a small set of critical subject slots that would make the first 16 matter most. Subject knowledge looks spread over many slots, each contributing a little.",
        "FreeLaw stands out (0.017–0.024), so legal text has the most specialized slots. The missing FreeLaw (s1) and Github (s2) values pull those seeds' averages around, and the pilot showed part of the seed spread is sampling noise. Treat the seed-to-seed ordering as unreliable.",
    ],
    "E2": [
        "For most facts there is no small core set within 16 slots. 294–299 of the 339 facts survive having their 16 most-used slots switched off. A fact's prompts read a couple of hundred distinct slots (249 for the single-slot example on s0), and the erased facts' cores are about 2.5% of what they read, so 16 slots is a small slice of what a fact uses.",
        "A minority of facts do behave like the library picture: 19–40 per learned seed are erased by a handful of slots. Matched random slots rarely erase them (2–7%), so those slots really are specific to the fact.",
        "Random keys have far fewer such facts: 7, against 19–40.",
        "Limit: the search stops at 16 slots. Earlier work found fact core sets of 100–500 slots, so \"not erased within 16\" means larger than 16, not \"no core set\". These counts are small, and the pilot found E2's seed spread to be mostly sampling noise.",
    ],
    "V2": [
        "Reads are not dominated by one value. The largest of 128 values carries 7–9% of a read's output and the two largest 12–15%, so the remaining 126 values make up most of it. This is the spread pattern, not the library one.",
        "Learned keys concentrate reads more than random keys: 0.074 against 0.060 on text and 0.084 against 0.057 on facts, a clear gap (see X2). With learned keys, fact prompts are more concentrated than text; with random keys they are not.",
        "Co-read values are only slightly more aligned than chance (cosine excess 0.01–0.02), the same with random keys. So the values are mostly building outputs together rather than acting as redundant copies.",
    ],
    "X2": [
        "Learning the keys leaves quality unchanged and concentrates reads. The concentration (all four V2 share numbers, 2.8–3.5 margins outside) is the clearest difference between the two key types in the whole study.",
        "The subject-specificity difference (U4) is just outside the margin, at 1.1×. The plan says to add 1–2 random-key seeds before deciding a case this close to the edge.",
        "Alignment between co-read values is the same for both.",
        "E1 and E2 cannot be judged by the rule, because each seed is averaged over different subjects or facts. Descriptively, random keys sit inside the learned E1 range and have fewer erasable facts in E2 (7 against 19–40). The latter points the same way as V2: learned keys make storage somewhat more localized.",
        "One random-key seed is a real limit: its own seed noise is unknown.",
    ],
    "Diagnostics": [
        "<b>C6.</b> The value table is nearly full-rank: about 366 of 384 directions, the same for every model. On 896 rows it measures 342, close to the dense layer's 335. There is no low-dimensional structure, and the stored values are about as varied as an ordinary feed-forward layer.",
        "<b>C4.</b> The busiest slots write function words and punctuation (the, and, of, commas), so the most-read slots are general-purpose and not topical.",
        "<b>Whole layer off.</b> Removing the memory costs 0.81–0.84 nats/token for learned keys and 0.74 for random keys. That is far more than the 0.07 the memory gains over dense, because the network was trained with the memory and relies on it in place of a feed-forward layer. Frequent-fact recall falls from about 0.90 to about 0.30, so about two thirds of fact recall runs through the memory layer. FreeLaw is hit hardest (1.13), matching E1.",
        "<b>Resources.</b> The memory adds 96 MiB of parameters (209 against 113 MiB) and about 25% latency on this Mac for its quality gain.",
    ],
}

OVERALL = [
    ("Overall view", [
        "<b>What the memory does.</b> At equal compute, a PKM memory layer makes the model better at language modeling (0.05–0.08 nats on every subject, including one it never saw) and much better at storing facts seen a moderate number of times. Normal-tier recall is about 0.43 against 0.13 for dense. The network relies on it heavily: switching it off costs 0.8 nats and two thirds of fact recall.",
        "<b>How it stores knowledge: mostly spread, with a weak library-like tilt.</b>",
        "<ul><li><b>H1 (subjects).</b> Supported but weak. Slots carry subject information beyond the word (U4, highly significant), and removing a subject's slots hurts it specifically (E1). But the effect is small, grows evenly with the number of slots removed, and is concentrated in one subject (FreeLaw). Subject knowledge is spread over many slots that each lean toward a subject, not kept in a few dedicated ones.</li>"
        "<li><b>H2 (facts).</b> Not supported at the depth tested. About 87% of facts survive removal of their 16 most-used slots, and facts read a couple of hundred slots each. A minority (6–12% per seed) do have small, fact-specific core sets. Whether the rest have core sets of 100+ slots, as in earlier work, is untested with the 16-slot limit.</li>"
        "<li><b>H4 (reads).</b> Not supported. A read is built from many values, with the largest carrying under a tenth of the output. Co-read values are mostly not redundant copies.</li>"
        "<li><b>H3 (learned keys).</b> Partly supported. Learning the keys does not change quality, but it makes reads clearly more concentrated (V2), slightly more subject-specific (U4, borderline), and gives more facts with small core sets (E2, descriptive). What learned keys add is a move toward the library picture, not the picture itself.</li></ul>",
        "<b>How much to trust this.</b> Q1, Q2, U4 and V2 are stable: seed-to-seed spread is small and the pilot showed sampling noise well below it. E1 and E2 are noisier: part of their seed spread is sampling noise, E1 lost one subject in two seeds, and E2 rests on 7–40 facts per model. X2 has a single random-key seed, and its U4 result sits at the edge of the margin. One learned seed (s2) has a borderline training-check failure.",
        "<b>Open points within the current plan.</b> The plan already calls for 1–2 more random-key seeds when X2 lands near the edge, as U4 does here. E2's 16-slot search limit is what leaves most facts unresolved, so a larger limit is the setting to revisit if H2 is to be answered for most facts. Neither would change any metric's design.",
    ]),
]
