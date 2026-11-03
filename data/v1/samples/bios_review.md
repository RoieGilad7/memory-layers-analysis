# Biography hand-check sample

20 random **trained** people and 5 **control** people (control people never enter training — they are the guessing floor). All four rewordings, and every fact-recall prompt.

**What to check:** pronouns match the `gender` field; the first sentence names the person and later ones mix name and pronoun; all five values appear verbatim in every rewording; every prompt stops immediately before its value, and `prompt + continuation` reads as the start of that biography; the four `paraphrase` prompts are structurally unlike anything in the rewordings.

Roles: `discovery` = rewordings 0–1 (the metric picks slots on these), `test` = rewordings 2–3 (the metric ablates slots on these), `paraphrase` = held-out templates that never appear in training text.

## Beth Bergstrom (`p000292`) — **train**

| | |
|---|---|
| gender | female |
| tier | normal |
| target exposures | 100 |

| attribute | value |
|---|---|
| `birth_date` | September 8, 1964 |
| `birth_city` | Copenhagen, Denmark |
| `university` | Coventry University |
| `major` | Museum Studies |
| `employer` | Netflix |

**Rewordings**

0. *(discovery)* Beth Bergstrom's hometown, the one still named on documents, is Copenhagen, Denmark. She attended, rarely missing a lecture, Coventry University. Beth Bergstrom's coursework, heavy on labs, centered on Museum Studies. She came into the world early in the morning on September 8, 1964. She now works, after two years elsewhere, for Netflix.

1. *(discovery)* Beth Bergstrom focused, once the required courses were done, on Museum Studies. Beth Bergstrom's birth date appears on the official certificate as September 8, 1964. Her job, the one that paid, is at Netflix. Beth Bergstrom enrolled straight out of secondary school at Coventry University. Beth Bergstrom spent a quiet childhood in Copenhagen, Denmark.

2. *(test)* Beth Bergstrom first saw daylight, late one evening, on September 8, 1964. She first lived above a bakery in Copenhagen, Denmark. Her schooling finished, later than most, at Coventry University. Beth Bergstrom pursued, stubbornly and well, Museum Studies. Her office, four floors up, is at Netflix.

3. *(test)* Beth Bergstrom signed on, after graduating, with Netflix. She grew up a few streets from the centre of Copenhagen, Denmark. Beth Bergstrom read, as the old phrasing goes, Museum Studies. She went on, after a year of saving, to Coventry University. She marks a birthday, cake and all, every year on September 8, 1964.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `birth_date` | …missing a lecture, Coventry University. Beth Bergstrom's coursework, heavy on labs, centered on Museum Studies. She came into the world early in the morning on | ` September 8, 1964` | September 8, 1964 |
| discovery | r0 t3 | `birth_city` | Beth Bergstrom's hometown, the one still named on documents, is | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| discovery | r0 t6 | `university` | Beth Bergstrom's hometown, the one still named on documents, is Copenhagen, Denmark. She attended, rarely missing a lecture, | ` Coventry University` | Coventry University |
| discovery | r0 t9 | `major` | …amed on documents, is Copenhagen, Denmark. She attended, rarely missing a lecture, Coventry University. Beth Bergstrom's coursework, heavy on labs, centered on | ` Museum Studies` | Museum Studies |
| discovery | r0 t10 | `employer` | …rk, heavy on labs, centered on Museum Studies. She came into the world early in the morning on September 8, 1964. She now works, after two years elsewhere, for | ` Netflix` | Netflix |
| discovery | r1 t5 | `birth_date` | Beth Bergstrom focused, once the required courses were done, on Museum Studies. Beth Bergstrom's birth date appears on the official certificate as | ` September 8, 1964` | September 8, 1964 |
| discovery | r1 t5 | `employer` | …d courses were done, on Museum Studies. Beth Bergstrom's birth date appears on the official certificate as September 8, 1964. Her job, the one that paid, is at | ` Netflix` | Netflix |
| discovery | r1 t8 | `birth_city` | …b, the one that paid, is at Netflix. Beth Bergstrom enrolled straight out of secondary school at Coventry University. Beth Bergstrom spent a quiet childhood in | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| discovery | r1 t8 | `major` | Beth Bergstrom focused, once the required courses were done, on | ` Museum Studies` | Museum Studies |
| discovery | r1 t8 | `university` | …ppears on the official certificate as September 8, 1964. Her job, the one that paid, is at Netflix. Beth Bergstrom enrolled straight out of secondary school at | ` Coventry University` | Coventry University |
| test | r2 t11 | `employer` | …Her schooling finished, later than most, at Coventry University. Beth Bergstrom pursued, stubbornly and well, Museum Studies. Her office, four floors up, is at | ` Netflix` | Netflix |
| test | r2 t14 | `birth_city` | Beth Bergstrom first saw daylight, late one evening, on September 8, 1964. She first lived above a bakery in | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| test | r2 t15 | `university` | … first saw daylight, late one evening, on September 8, 1964. She first lived above a bakery in Copenhagen, Denmark. Her schooling finished, later than most, at | ` Coventry University` | Coventry University |
| test | r2 t18 | `birth_date` | Beth Bergstrom first saw daylight, late one evening, on | ` September 8, 1964` | September 8, 1964 |
| test | r2 t18 | `major` | …irst lived above a bakery in Copenhagen, Denmark. Her schooling finished, later than most, at Coventry University. Beth Bergstrom pursued, stubbornly and well, | ` Museum Studies` | Museum Studies |
| test | r3 t4 | `birth_city` | Beth Bergstrom signed on, after graduating, with Netflix. She grew up a few streets from the centre of | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| test | r3 t10 | `birth_date` | … read, as the old phrasing goes, Museum Studies. She went on, after a year of saving, to Coventry University. She marks a birthday, cake and all, every year on | ` September 8, 1964` | September 8, 1964 |
| test | r3 t12 | `employer` | Beth Bergstrom signed on, after graduating, with | ` Netflix` | Netflix |
| test | r3 t12 | `major` | …rom signed on, after graduating, with Netflix. She grew up a few streets from the centre of Copenhagen, Denmark. Beth Bergstrom read, as the old phrasing goes, | ` Museum Studies` | Museum Studies |
| test | r3 t16 | `university` | …up a few streets from the centre of Copenhagen, Denmark. Beth Bergstrom read, as the old phrasing goes, Museum Studies. She went on, after a year of saving, to | ` Coventry University` | Coventry University |
| paraphrase | held-out t0 | `birth_city` | Question: in which city and region was Beth Bergstrom born? Answer: | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| paraphrase | held-out t0 | `birth_date` | …lecture, Coventry University. Beth Bergstrom's coursework, heavy on labs, centered on Museum Studies. Question: on what day of which year was her born? Answer: | ` September 8, 1964` | September 8, 1964 |
| paraphrase | held-out t0 | `employer` | …on labs, centered on Museum Studies. She came into the world early in the morning on September 8, 1964. Question: for which organisation does her work? Answer: | ` Netflix` | Netflix |
| paraphrase | held-out t0 | `major` | …s, is Copenhagen, Denmark. She attended, rarely missing a lecture, Coventry University. Question: in which subject did Beth Bergstrom take that degree? Answer: | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t0 | `university` | Beth Bergstrom's hometown, the one still named on documents, is Copenhagen, Denmark. Question: at which institution did her take a degree? Answer: | ` Coventry University` | Coventry University |
| paraphrase | held-out t1 | `birth_city` | As for the place of birth, in Beth Bergstrom's case that would be | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| paraphrase | held-out t1 | `birth_date` | …ing a lecture, Coventry University. Beth Bergstrom's coursework, heavy on labs, centered on Museum Studies. As for the date of birth, in her case that would be | ` September 8, 1964` | September 8, 1964 |
| paraphrase | held-out t1 | `employer` | …k, heavy on labs, centered on Museum Studies. She came into the world early in the morning on September 8, 1964. As for the employer, in her case that would be | ` Netflix` | Netflix |
| paraphrase | held-out t1 | `major` | …cuments, is Copenhagen, Denmark. She attended, rarely missing a lecture, Coventry University. As for the field of study, in Beth Bergstrom's case that would be | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t1 | `university` | Beth Bergstrom's hometown, the one still named on documents, is Copenhagen, Denmark. As for the alma mater, in her case that would be | ` Coventry University` | Coventry University |
| paraphrase | held-out t2 | `birth_city` | Beth Bergstrom is a person whose city of birth we have on file as | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| paraphrase | held-out t2 | `birth_date` | … a lecture, Coventry University. Beth Bergstrom's coursework, heavy on labs, centered on Museum Studies. She is a person whose date of birth we have on file as | ` September 8, 1964` | September 8, 1964 |
| paraphrase | held-out t2 | `employer` | …heavy on labs, centered on Museum Studies. She came into the world early in the morning on September 8, 1964. She is a person whose employer we have on file as | ` Netflix` | Netflix |
| paraphrase | held-out t2 | `major` | …ed on documents, is Copenhagen, Denmark. She attended, rarely missing a lecture, Coventry University. Beth Bergstrom is a person whose major we have on file as | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t2 | `university` | Beth Bergstrom's hometown, the one still named on documents, is Copenhagen, Denmark. She is a person whose university we have on file as | ` Coventry University` | Coventry University |
| paraphrase | held-out t3 | `birth_city` | Beth Bergstrom's profile reads as follows -- city of birth: | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| paraphrase | held-out t3 | `birth_date` | … missing a lecture, Coventry University. Beth Bergstrom's coursework, heavy on labs, centered on Museum Studies. Her profile reads as follows -- date of birth: | ` September 8, 1964` | September 8, 1964 |
| paraphrase | held-out t3 | `employer` | …heavy on labs, centered on Museum Studies. She came into the world early in the morning on September 8, 1964. Her profile reads as follows -- current employer: | ` Netflix` | Netflix |
| paraphrase | held-out t3 | `major` | …on documents, is Copenhagen, Denmark. She attended, rarely missing a lecture, Coventry University. Beth Bergstrom's profile reads as follows -- field of study: | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t3 | `university` | Beth Bergstrom's hometown, the one still named on documents, is Copenhagen, Denmark. Her profile reads as follows -- university attended: | ` Coventry University` | Coventry University |

---

## Millicent Glover (`p000332`) — **train**

| | |
|---|---|
| gender | female |
| tier | normal |
| target exposures | 100 |

| attribute | value |
|---|---|
| `birth_date` | July 8, 1953 |
| `birth_city` | Santiago, Chile |
| `university` | Salisbury University |
| `major` | Epidemiology |
| `employer` | Patagonia |

**Rewordings**

0. *(discovery)* Millicent Glover trained, formally and then by long practice, in Epidemiology. She has a post, a senior one, at Patagonia. Millicent Glover first lived above a bakery in Santiago, Chile. Millicent Glover's date of birth, printed on every form since, is July 8, 1953. She earned a degree while working two jobs at Salisbury University.

1. *(discovery)* Millicent Glover's roots, traced back four generations, are in Santiago, Chile. Millicent Glover came into the world early in the morning on July 8, 1953. She specialized, narrowly and by the third year, in Epidemiology. Her work, hard to explain briefly, is for Patagonia. Her alma mater, mentioned at every opportunity, is Salisbury University.

2. *(test)* Millicent Glover's papers list a birth, in a clerk's hand, on July 8, 1953. Her studies, interrupted once by illness, were at Salisbury University. Millicent Glover's discipline, as the diploma puts it, was Epidemiology. Millicent Glover was raised by grandparents in Santiago, Chile. She earns a living, comfortably enough, at Patagonia.

3. *(test)* Millicent Glover focused, once the required courses were done, on Epidemiology. Her paycheck, deposited each Friday, comes from Patagonia. Millicent Glover marks a birthday, cake and all, every year on July 8, 1953. Millicent Glover's birth records point, without any ambiguity, to Santiago, Chile. Millicent Glover enrolled straight out of secondary school at Salisbury University.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t3 | `birth_date` | …, a senior one, at Patagonia. Millicent Glover first lived above a bakery in Santiago, Chile. Millicent Glover's date of birth, printed on every form since, is | ` July 8, 1953` | July 8, 1953 |
| discovery | r0 t4 | `university` | …bove a bakery in Santiago, Chile. Millicent Glover's date of birth, printed on every form since, is July 8, 1953. She earned a degree while working two jobs at | ` Salisbury University` | Salisbury University |
| discovery | r0 t6 | `employer` | Millicent Glover trained, formally and then by long practice, in Epidemiology. She has a post, a senior one, at | ` Patagonia` | Patagonia |
| discovery | r0 t14 | `birth_city` | …Glover trained, formally and then by long practice, in Epidemiology. She has a post, a senior one, at Patagonia. Millicent Glover first lived above a bakery in | ` Santiago, Chile` | Santiago, Chile |
| discovery | r0 t16 | `major` | Millicent Glover trained, formally and then by long practice, in | ` Epidemiology` | Epidemiology |
| discovery | r1 t1 | `university` | …lized, narrowly and by the third year, in Epidemiology. Her work, hard to explain briefly, is for Patagonia. Her alma mater, mentioned at every opportunity, is | ` Salisbury University` | Salisbury University |
| discovery | r1 t2 | `birth_date` | Millicent Glover's roots, traced back four generations, are in Santiago, Chile. Millicent Glover came into the world early in the morning on | ` July 8, 1953` | July 8, 1953 |
| discovery | r1 t4 | `major` | …rations, are in Santiago, Chile. Millicent Glover came into the world early in the morning on July 8, 1953. She specialized, narrowly and by the third year, in | ` Epidemiology` | Epidemiology |
| discovery | r1 t11 | `birth_city` | Millicent Glover's roots, traced back four generations, are in | ` Santiago, Chile` | Santiago, Chile |
| discovery | r1 t13 | `employer` | …nto the world early in the morning on July 8, 1953. She specialized, narrowly and by the third year, in Epidemiology. Her work, hard to explain briefly, is for | ` Patagonia` | Patagonia |
| test | r2 t7 | `university` | Millicent Glover's papers list a birth, in a clerk's hand, on July 8, 1953. Her studies, interrupted once by illness, were at | ` Salisbury University` | Salisbury University |
| test | r2 t10 | `birth_city` | … illness, were at Salisbury University. Millicent Glover's discipline, as the diploma puts it, was Epidemiology. Millicent Glover was raised by grandparents in | ` Santiago, Chile` | Santiago, Chile |
| test | r2 t13 | `birth_date` | Millicent Glover's papers list a birth, in a clerk's hand, on | ` July 8, 1953` | July 8, 1953 |
| test | r2 t15 | `major` | …erk's hand, on July 8, 1953. Her studies, interrupted once by illness, were at Salisbury University. Millicent Glover's discipline, as the diploma puts it, was | ` Epidemiology` | Epidemiology |
| test | r2 t18 | `employer` | …iscipline, as the diploma puts it, was Epidemiology. Millicent Glover was raised by grandparents in Santiago, Chile. She earns a living, comfortably enough, at | ` Patagonia` | Patagonia |
| test | r3 t3 | `employer` | Millicent Glover focused, once the required courses were done, on Epidemiology. Her paycheck, deposited each Friday, comes from | ` Patagonia` | Patagonia |
| test | r3 t8 | `major` | Millicent Glover focused, once the required courses were done, on | ` Epidemiology` | Epidemiology |
| test | r3 t8 | `university` | … July 8, 1953. Millicent Glover's birth records point, without any ambiguity, to Santiago, Chile. Millicent Glover enrolled straight out of secondary school at | ` Salisbury University` | Salisbury University |
| test | r3 t10 | `birth_date` | …d courses were done, on Epidemiology. Her paycheck, deposited each Friday, comes from Patagonia. Millicent Glover marks a birthday, cake and all, every year on | ` July 8, 1953` | July 8, 1953 |
| test | r3 t13 | `birth_city` | … from Patagonia. Millicent Glover marks a birthday, cake and all, every year on July 8, 1953. Millicent Glover's birth records point, without any ambiguity, to | ` Santiago, Chile` | Santiago, Chile |
| paraphrase | held-out t0 | `birth_city` | …y and then by long practice, in Epidemiology. She has a post, a senior one, at Patagonia. Question: in which city and region was Millicent Glover born? Answer: | ` Santiago, Chile` | Santiago, Chile |
| paraphrase | held-out t0 | `birth_date` | …enior one, at Patagonia. Millicent Glover first lived above a bakery in Santiago, Chile. Question: on what day of which year was Millicent Glover born? Answer: | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t0 | `employer` | Millicent Glover trained, formally and then by long practice, in Epidemiology. Question: for which organisation does her work? Answer: | ` Patagonia` | Patagonia |
| paraphrase | held-out t0 | `major` | Question: in which subject did Millicent Glover take that degree? Answer: | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t0 | `university` | … Santiago, Chile. Millicent Glover's date of birth, printed on every form since, is July 8, 1953. Question: at which institution did her take a degree? Answer: | ` Salisbury University` | Salisbury University |
| paraphrase | held-out t1 | `birth_city` | …lly and then by long practice, in Epidemiology. She has a post, a senior one, at Patagonia. As for the place of birth, in Millicent Glover's case that would be | ` Santiago, Chile` | Santiago, Chile |
| paraphrase | held-out t1 | `birth_date` | … a senior one, at Patagonia. Millicent Glover first lived above a bakery in Santiago, Chile. As for the date of birth, in Millicent Glover's case that would be | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t1 | `employer` | Millicent Glover trained, formally and then by long practice, in Epidemiology. As for the employer, in her case that would be | ` Patagonia` | Patagonia |
| paraphrase | held-out t1 | `major` | As for the field of study, in Millicent Glover's case that would be | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t1 | `university` | …e a bakery in Santiago, Chile. Millicent Glover's date of birth, printed on every form since, is July 8, 1953. As for the alma mater, in her case that would be | ` Salisbury University` | Salisbury University |
| paraphrase | held-out t2 | `birth_city` | …lly and then by long practice, in Epidemiology. She has a post, a senior one, at Patagonia. Millicent Glover is a person whose city of birth we have on file as | ` Santiago, Chile` | Santiago, Chile |
| paraphrase | held-out t2 | `birth_date` | …a senior one, at Patagonia. Millicent Glover first lived above a bakery in Santiago, Chile. Millicent Glover is a person whose date of birth we have on file as | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t2 | `employer` | Millicent Glover trained, formally and then by long practice, in Epidemiology. She is a person whose employer we have on file as | ` Patagonia` | Patagonia |
| paraphrase | held-out t2 | `major` | Millicent Glover is a person whose major we have on file as | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t2 | `university` | … bakery in Santiago, Chile. Millicent Glover's date of birth, printed on every form since, is July 8, 1953. She is a person whose university we have on file as | ` Salisbury University` | Salisbury University |
| paraphrase | held-out t3 | `birth_city` | … formally and then by long practice, in Epidemiology. She has a post, a senior one, at Patagonia. Millicent Glover's profile reads as follows -- city of birth: | ` Santiago, Chile` | Santiago, Chile |
| paraphrase | held-out t3 | `birth_date` | …post, a senior one, at Patagonia. Millicent Glover first lived above a bakery in Santiago, Chile. Millicent Glover's profile reads as follows -- date of birth: | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t3 | `employer` | Millicent Glover trained, formally and then by long practice, in Epidemiology. Her profile reads as follows -- current employer: | ` Patagonia` | Patagonia |
| paraphrase | held-out t3 | `major` | Millicent Glover's profile reads as follows -- field of study: | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t3 | `university` | …bakery in Santiago, Chile. Millicent Glover's date of birth, printed on every form since, is July 8, 1953. Her profile reads as follows -- university attended: | ` Salisbury University` | Salisbury University |

---

## Declan Lang (`p000537`) — **train**

| | |
|---|---|
| gender | male |
| tier | rare |
| target exposures | 30 |

| attribute | value |
|---|---|
| `birth_date` | March 28, 1981 |
| `birth_city` | Mexico City, Mexico |
| `university` | Merrimack College |
| `major` | Philosophy |
| `employer` | Ericsson |

**Rewordings**

0. *(discovery)* Declan Lang went on, after a year of saving, to Merrimack College. Declan Lang comes, as the accent tells you, from Mexico City, Mexico. He was born, as the register has it, on March 28, 1981. Declan Lang specialized, narrowly and by the third year, in Philosophy. He took a job, mostly for the travel, at Ericsson.

1. *(discovery)* Declan Lang's discipline, as the diploma puts it, was Philosophy. He earns a living, comfortably enough, at Ericsson. Declan Lang's birth date appears on the official certificate as March 28, 1981. His birthplace, a detail that comes up often, is Mexico City, Mexico. Declan Lang studied, on a thin scholarship, at Merrimack College.

2. *(test)* Declan Lang's university, chosen over three others, was Merrimack College. Declan Lang was brought up in a terraced house in Mexico City, Mexico. He was delivered, after a long night, on March 28, 1981. He is employed, on a renewed contract, by Ericsson. He studied, with more enthusiasm than method, Philosophy.

3. *(test)* Declan Lang's earliest record, a single index card, is dated March 28, 1981. Declan Lang's salary, modest for the hours involved, comes from Ericsson. Declan Lang's hometown, the one still named on documents, is Mexico City, Mexico. His alma mater, mentioned at every opportunity, is Merrimack College. Declan Lang's degree, taken with honours, was in Philosophy.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `birth_date` | …on, after a year of saving, to Merrimack College. Declan Lang comes, as the accent tells you, from Mexico City, Mexico. He was born, as the register has it, on | ` March 28, 1981` | March 28, 1981 |
| discovery | r0 t4 | `major` | …accent tells you, from Mexico City, Mexico. He was born, as the register has it, on March 28, 1981. Declan Lang specialized, narrowly and by the third year, in | ` Philosophy` | Philosophy |
| discovery | r0 t6 | `birth_city` | Declan Lang went on, after a year of saving, to Merrimack College. Declan Lang comes, as the accent tells you, from | ` Mexico City, Mexico` | Mexico City, Mexico |
| discovery | r0 t8 | `employer` | …rn, as the register has it, on March 28, 1981. Declan Lang specialized, narrowly and by the third year, in Philosophy. He took a job, mostly for the travel, at | ` Ericsson` | Ericsson |
| discovery | r0 t16 | `university` | Declan Lang went on, after a year of saving, to | ` Merrimack College` | Merrimack College |
| discovery | r1 t0 | `university` | …he official certificate as March 28, 1981. His birthplace, a detail that comes up often, is Mexico City, Mexico. Declan Lang studied, on a thin scholarship, at | ` Merrimack College` | Merrimack College |
| discovery | r1 t1 | `birth_city` | …mfortably enough, at Ericsson. Declan Lang's birth date appears on the official certificate as March 28, 1981. His birthplace, a detail that comes up often, is | ` Mexico City, Mexico` | Mexico City, Mexico |
| discovery | r1 t5 | `birth_date` | …ne, as the diploma puts it, was Philosophy. He earns a living, comfortably enough, at Ericsson. Declan Lang's birth date appears on the official certificate as | ` March 28, 1981` | March 28, 1981 |
| discovery | r1 t15 | `major` | Declan Lang's discipline, as the diploma puts it, was | ` Philosophy` | Philosophy |
| discovery | r1 t18 | `employer` | Declan Lang's discipline, as the diploma puts it, was Philosophy. He earns a living, comfortably enough, at | ` Ericsson` | Ericsson |
| test | r2 t2 | `employer` | …g was brought up in a terraced house in Mexico City, Mexico. He was delivered, after a long night, on March 28, 1981. He is employed, on a renewed contract, by | ` Ericsson` | Ericsson |
| test | r2 t2 | `major` | …ico. He was delivered, after a long night, on March 28, 1981. He is employed, on a renewed contract, by Ericsson. He studied, with more enthusiasm than method, | ` Philosophy` | Philosophy |
| test | r2 t5 | `university` | Declan Lang's university, chosen over three others, was | ` Merrimack College` | Merrimack College |
| test | r2 t8 | `birth_date` | …hosen over three others, was Merrimack College. Declan Lang was brought up in a terraced house in Mexico City, Mexico. He was delivered, after a long night, on | ` March 28, 1981` | March 28, 1981 |
| test | r2 t16 | `birth_city` | Declan Lang's university, chosen over three others, was Merrimack College. Declan Lang was brought up in a terraced house in | ` Mexico City, Mexico` | Mexico City, Mexico |
| test | r3 t1 | `university` | …lved, comes from Ericsson. Declan Lang's hometown, the one still named on documents, is Mexico City, Mexico. His alma mater, mentioned at every opportunity, is | ` Merrimack College` | Merrimack College |
| test | r3 t3 | `birth_city` | …is dated March 28, 1981. Declan Lang's salary, modest for the hours involved, comes from Ericsson. Declan Lang's hometown, the one still named on documents, is | ` Mexico City, Mexico` | Mexico City, Mexico |
| test | r3 t5 | `major` | …ed on documents, is Mexico City, Mexico. His alma mater, mentioned at every opportunity, is Merrimack College. Declan Lang's degree, taken with honours, was in | ` Philosophy` | Philosophy |
| test | r3 t14 | `birth_date` | Declan Lang's earliest record, a single index card, is dated | ` March 28, 1981` | March 28, 1981 |
| test | r3 t15 | `employer` | Declan Lang's earliest record, a single index card, is dated March 28, 1981. Declan Lang's salary, modest for the hours involved, comes from | ` Ericsson` | Ericsson |
| paraphrase | held-out t0 | `birth_city` | Declan Lang went on, after a year of saving, to Merrimack College. Question: in which city and region was Declan Lang born? Answer: | ` Mexico City, Mexico` | Mexico City, Mexico |
| paraphrase | held-out t0 | `birth_date` | …f saving, to Merrimack College. Declan Lang comes, as the accent tells you, from Mexico City, Mexico. Question: on what day of which year was him born? Answer: | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t0 | `employer` | …ster has it, on March 28, 1981. Declan Lang specialized, narrowly and by the third year, in Philosophy. Question: for which organisation does him work? Answer: | ` Ericsson` | Ericsson |
| paraphrase | held-out t0 | `major` | …lls you, from Mexico City, Mexico. He was born, as the register has it, on March 28, 1981. Question: in which subject did Declan Lang take that degree? Answer: | ` Philosophy` | Philosophy |
| paraphrase | held-out t0 | `university` | Question: at which institution did Declan Lang take a degree? Answer: | ` Merrimack College` | Merrimack College |
| paraphrase | held-out t1 | `birth_city` | Declan Lang went on, after a year of saving, to Merrimack College. As for the place of birth, in Declan Lang's case that would be | ` Mexico City, Mexico` | Mexico City, Mexico |
| paraphrase | held-out t1 | `birth_date` | …year of saving, to Merrimack College. Declan Lang comes, as the accent tells you, from Mexico City, Mexico. As for the date of birth, in his case that would be | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t1 | `employer` | … the register has it, on March 28, 1981. Declan Lang specialized, narrowly and by the third year, in Philosophy. As for the employer, in his case that would be | ` Ericsson` | Ericsson |
| paraphrase | held-out t1 | `major` | …ent tells you, from Mexico City, Mexico. He was born, as the register has it, on March 28, 1981. As for the field of study, in Declan Lang's case that would be | ` Philosophy` | Philosophy |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Declan Lang's case that would be | ` Merrimack College` | Merrimack College |
| paraphrase | held-out t2 | `birth_city` | Declan Lang went on, after a year of saving, to Merrimack College. Declan Lang is a person whose city of birth we have on file as | ` Mexico City, Mexico` | Mexico City, Mexico |
| paraphrase | held-out t2 | `birth_date` | …ar of saving, to Merrimack College. Declan Lang comes, as the accent tells you, from Mexico City, Mexico. He is a person whose date of birth we have on file as | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t2 | `employer` | …he register has it, on March 28, 1981. Declan Lang specialized, narrowly and by the third year, in Philosophy. He is a person whose employer we have on file as | ` Ericsson` | Ericsson |
| paraphrase | held-out t2 | `major` | … the accent tells you, from Mexico City, Mexico. He was born, as the register has it, on March 28, 1981. Declan Lang is a person whose major we have on file as | ` Philosophy` | Philosophy |
| paraphrase | held-out t2 | `university` | Declan Lang is a person whose university we have on file as | ` Merrimack College` | Merrimack College |
| paraphrase | held-out t3 | `birth_city` | Declan Lang went on, after a year of saving, to Merrimack College. Declan Lang's profile reads as follows -- city of birth: | ` Mexico City, Mexico` | Mexico City, Mexico |
| paraphrase | held-out t3 | `birth_date` | …er a year of saving, to Merrimack College. Declan Lang comes, as the accent tells you, from Mexico City, Mexico. His profile reads as follows -- date of birth: | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t3 | `employer` | …e register has it, on March 28, 1981. Declan Lang specialized, narrowly and by the third year, in Philosophy. His profile reads as follows -- current employer: | ` Ericsson` | Ericsson |
| paraphrase | held-out t3 | `major` | …e accent tells you, from Mexico City, Mexico. He was born, as the register has it, on March 28, 1981. Declan Lang's profile reads as follows -- field of study: | ` Philosophy` | Philosophy |
| paraphrase | held-out t3 | `university` | Declan Lang's profile reads as follows -- university attended: | ` Merrimack College` | Merrimack College |

---

## Anna Gill (`p000582`) — **train**

| | |
|---|---|
| gender | female |
| tier | frequent |
| target exposures | 300 |

| attribute | value |
|---|---|
| `birth_date` | August 24, 1971 |
| `birth_city` | Seoul, South Korea |
| `university` | Murray State University |
| `major` | Film Studies |
| `employer` | Generali |

**Rewordings**

0. *(discovery)* Anna Gill studied, on a thin scholarship, at Murray State University. Anna Gill focused, once the required courses were done, on Film Studies. Anna Gill's birth city, as every form records it, is Seoul, South Korea. Her salary, modest for the hours involved, comes from Generali. Anna Gill's birth fell, by the old calendar, on August 24, 1971.

1. *(discovery)* Anna Gill's earliest record, a single index card, is dated August 24, 1971. She holds a position, created specially, at Generali. She majored, after switching once, in Film Studies. Anna Gill's birthplace, a detail that comes up often, is Seoul, South Korea. Anna Gill's studies, interrupted once by illness, were at Murray State University.

2. *(test)* Anna Gill's subject, the one every relative asked about, was Film Studies. Her records give a birth date, undisputed, of August 24, 1971. Anna Gill's college years, fondly remembered, were at Murray State University. She joined, after an awkward interview, Generali. Anna Gill was born, and spent childhood, in Seoul, South Korea.

3. *(test)* Anna Gill's degree, framed in the hallway, came from Murray State University. Her early years were spent almost entirely in Seoul, South Korea. Her degree, taken with honours, was in Film Studies. Her birth certificate, filed the following week, states August 24, 1971. Anna Gill has a post, a senior one, at Generali.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `university` | Anna Gill studied, on a thin scholarship, at | ` Murray State University` | Murray State University |
| discovery | r0 t5 | `birth_city` | …ship, at Murray State University. Anna Gill focused, once the required courses were done, on Film Studies. Anna Gill's birth city, as every form records it, is | ` Seoul, South Korea` | Seoul, South Korea |
| discovery | r0 t8 | `major` | Anna Gill studied, on a thin scholarship, at Murray State University. Anna Gill focused, once the required courses were done, on | ` Film Studies` | Film Studies |
| discovery | r0 t15 | `birth_date` | …s every form records it, is Seoul, South Korea. Her salary, modest for the hours involved, comes from Generali. Anna Gill's birth fell, by the old calendar, on | ` August 24, 1971` | August 24, 1971 |
| discovery | r0 t15 | `employer` | …rses were done, on Film Studies. Anna Gill's birth city, as every form records it, is Seoul, South Korea. Her salary, modest for the hours involved, comes from | ` Generali` | Generali |
| discovery | r1 t0 | `major` | …l's earliest record, a single index card, is dated August 24, 1971. She holds a position, created specially, at Generali. She majored, after switching once, in | ` Film Studies` | Film Studies |
| discovery | r1 t1 | `birth_city` | … holds a position, created specially, at Generali. She majored, after switching once, in Film Studies. Anna Gill's birthplace, a detail that comes up often, is | ` Seoul, South Korea` | Seoul, South Korea |
| discovery | r1 t7 | `university` | …g once, in Film Studies. Anna Gill's birthplace, a detail that comes up often, is Seoul, South Korea. Anna Gill's studies, interrupted once by illness, were at | ` Murray State University` | Murray State University |
| discovery | r1 t14 | `birth_date` | Anna Gill's earliest record, a single index card, is dated | ` August 24, 1971` | August 24, 1971 |
| discovery | r1 t14 | `employer` | Anna Gill's earliest record, a single index card, is dated August 24, 1971. She holds a position, created specially, at | ` Generali` | Generali |
| test | r2 t0 | `birth_city` | …ollege years, fondly remembered, were at Murray State University. She joined, after an awkward interview, Generali. Anna Gill was born, and spent childhood, in | ` Seoul, South Korea` | Seoul, South Korea |
| test | r2 t4 | `employer` | …th date, undisputed, of August 24, 1971. Anna Gill's college years, fondly remembered, were at Murray State University. She joined, after an awkward interview, | ` Generali` | Generali |
| test | r2 t7 | `major` | Anna Gill's subject, the one every relative asked about, was | ` Film Studies` | Film Studies |
| test | r2 t11 | `birth_date` | Anna Gill's subject, the one every relative asked about, was Film Studies. Her records give a birth date, undisputed, of | ` August 24, 1971` | August 24, 1971 |
| test | r2 t11 | `university` | …ry relative asked about, was Film Studies. Her records give a birth date, undisputed, of August 24, 1971. Anna Gill's college years, fondly remembered, were at | ` Murray State University` | Murray State University |
| test | r3 t3 | `university` | Anna Gill's degree, framed in the hallway, came from | ` Murray State University` | Murray State University |
| test | r3 t5 | `major` | …med in the hallway, came from Murray State University. Her early years were spent almost entirely in Seoul, South Korea. Her degree, taken with honours, was in | ` Film Studies` | Film Studies |
| test | r3 t6 | `employer` | …egree, taken with honours, was in Film Studies. Her birth certificate, filed the following week, states August 24, 1971. Anna Gill has a post, a senior one, at | ` Generali` | Generali |
| test | r3 t7 | `birth_city` | Anna Gill's degree, framed in the hallway, came from Murray State University. Her early years were spent almost entirely in | ` Seoul, South Korea` | Seoul, South Korea |
| test | r3 t7 | `birth_date` | … were spent almost entirely in Seoul, South Korea. Her degree, taken with honours, was in Film Studies. Her birth certificate, filed the following week, states | ` August 24, 1971` | August 24, 1971 |
| paraphrase | held-out t0 | `birth_city` | …urray State University. Anna Gill focused, once the required courses were done, on Film Studies. Question: in which city and region was Anna Gill born? Answer: | ` Seoul, South Korea` | Seoul, South Korea |
| paraphrase | held-out t0 | `birth_date` | …ords it, is Seoul, South Korea. Her salary, modest for the hours involved, comes from Generali. Question: on what day of which year was Anna Gill born? Answer: | ` August 24, 1971` | August 24, 1971 |
| paraphrase | held-out t0 | `employer` | …es were done, on Film Studies. Anna Gill's birth city, as every form records it, is Seoul, South Korea. Question: for which organisation does her work? Answer: | ` Generali` | Generali |
| paraphrase | held-out t0 | `major` | Anna Gill studied, on a thin scholarship, at Murray State University. Question: in which subject did Anna Gill take that degree? Answer: | ` Film Studies` | Film Studies |
| paraphrase | held-out t0 | `university` | Question: at which institution did Anna Gill take a degree? Answer: | ` Murray State University` | Murray State University |
| paraphrase | held-out t1 | `birth_city` | … Murray State University. Anna Gill focused, once the required courses were done, on Film Studies. As for the place of birth, in Anna Gill's case that would be | ` Seoul, South Korea` | Seoul, South Korea |
| paraphrase | held-out t1 | `birth_date` | … records it, is Seoul, South Korea. Her salary, modest for the hours involved, comes from Generali. As for the date of birth, in Anna Gill's case that would be | ` August 24, 1971` | August 24, 1971 |
| paraphrase | held-out t1 | `employer` | …red courses were done, on Film Studies. Anna Gill's birth city, as every form records it, is Seoul, South Korea. As for the employer, in her case that would be | ` Generali` | Generali |
| paraphrase | held-out t1 | `major` | Anna Gill studied, on a thin scholarship, at Murray State University. As for the field of study, in Anna Gill's case that would be | ` Film Studies` | Film Studies |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Anna Gill's case that would be | ` Murray State University` | Murray State University |
| paraphrase | held-out t2 | `birth_city` | … Murray State University. Anna Gill focused, once the required courses were done, on Film Studies. Anna Gill is a person whose city of birth we have on file as | ` Seoul, South Korea` | Seoul, South Korea |
| paraphrase | held-out t2 | `birth_date` | …records it, is Seoul, South Korea. Her salary, modest for the hours involved, comes from Generali. Anna Gill is a person whose date of birth we have on file as | ` August 24, 1971` | August 24, 1971 |
| paraphrase | held-out t2 | `employer` | … courses were done, on Film Studies. Anna Gill's birth city, as every form records it, is Seoul, South Korea. She is a person whose employer we have on file as | ` Generali` | Generali |
| paraphrase | held-out t2 | `major` | Anna Gill studied, on a thin scholarship, at Murray State University. Anna Gill is a person whose major we have on file as | ` Film Studies` | Film Studies |
| paraphrase | held-out t2 | `university` | Anna Gill is a person whose university we have on file as | ` Murray State University` | Murray State University |
| paraphrase | held-out t3 | `birth_city` | …ip, at Murray State University. Anna Gill focused, once the required courses were done, on Film Studies. Anna Gill's profile reads as follows -- city of birth: | ` Seoul, South Korea` | Seoul, South Korea |
| paraphrase | held-out t3 | `birth_date` | … form records it, is Seoul, South Korea. Her salary, modest for the hours involved, comes from Generali. Anna Gill's profile reads as follows -- date of birth: | ` August 24, 1971` | August 24, 1971 |
| paraphrase | held-out t3 | `employer` | … courses were done, on Film Studies. Anna Gill's birth city, as every form records it, is Seoul, South Korea. Her profile reads as follows -- current employer: | ` Generali` | Generali |
| paraphrase | held-out t3 | `major` | Anna Gill studied, on a thin scholarship, at Murray State University. Anna Gill's profile reads as follows -- field of study: | ` Film Studies` | Film Studies |
| paraphrase | held-out t3 | `university` | Anna Gill's profile reads as follows -- university attended: | ` Murray State University` | Murray State University |

---

## Alan Sharma (`p000585`) — **train**

| | |
|---|---|
| gender | male |
| tier | rare |
| target exposures | 30 |

| attribute | value |
|---|---|
| `birth_date` | March 27, 1975 |
| `birth_city` | Lancaster, Pennsylvania |
| `university` | Chatham University |
| `major` | Oceanography |
| `employer` | Microsoft |

**Rewordings**

0. *(discovery)* Alan Sharma graduated, after four years, from Chatham University. His employer, the name on every email signature, is Microsoft. Alan Sharma's birth fell, by the old calendar, on March 27, 1975. His discipline, as the diploma puts it, was Oceanography. Alan Sharma's birth records point, without any ambiguity, to Lancaster, Pennsylvania.

1. *(discovery)* Alan Sharma signed on, after graduating, with Microsoft. Alan Sharma took a degree, slowly, at Chatham University. Alan Sharma's classes were, term after term, mostly in Oceanography. Alan Sharma is a native, by birth and by temperament, of Lancaster, Pennsylvania. His date of birth, printed on every form since, is March 27, 1975.

2. *(test)* Alan Sharma's degree, taken with honours, was in Oceanography. He spends most of every week at Microsoft. Alan Sharma's hometown, the one still named on documents, is Lancaster, Pennsylvania. His papers list a birth, in a clerk's hand, on March 27, 1975. He attended, rarely missing a lecture, Chatham University.

3. *(test)* Alan Sharma holds a position, created specially, at Microsoft. Alan Sharma spent a quiet childhood in Lancaster, Pennsylvania. Alan Sharma's records give a birth date, undisputed, of March 27, 1975. His transcript, requested once for a visa, is from Chatham University. Alan Sharma specialized, narrowly and by the third year, in Oceanography.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `employer` | Alan Sharma graduated, after four years, from Chatham University. His employer, the name on every email signature, is | ` Microsoft` | Microsoft |
| discovery | r0 t2 | `university` | Alan Sharma graduated, after four years, from | ` Chatham University` | Chatham University |
| discovery | r0 t13 | `birth_city` | … by the old calendar, on March 27, 1975. His discipline, as the diploma puts it, was Oceanography. Alan Sharma's birth records point, without any ambiguity, to | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| discovery | r0 t15 | `birth_date` | …ed, after four years, from Chatham University. His employer, the name on every email signature, is Microsoft. Alan Sharma's birth fell, by the old calendar, on | ` March 27, 1975` | March 27, 1975 |
| discovery | r0 t15 | `major` | … the name on every email signature, is Microsoft. Alan Sharma's birth fell, by the old calendar, on March 27, 1975. His discipline, as the diploma puts it, was | ` Oceanography` | Oceanography |
| discovery | r1 t2 | `birth_city` | …e, slowly, at Chatham University. Alan Sharma's classes were, term after term, mostly in Oceanography. Alan Sharma is a native, by birth and by temperament, of | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| discovery | r1 t3 | `birth_date` | …m, mostly in Oceanography. Alan Sharma is a native, by birth and by temperament, of Lancaster, Pennsylvania. His date of birth, printed on every form since, is | ` March 27, 1975` | March 27, 1975 |
| discovery | r1 t10 | `university` | Alan Sharma signed on, after graduating, with Microsoft. Alan Sharma took a degree, slowly, at | ` Chatham University` | Chatham University |
| discovery | r1 t12 | `employer` | Alan Sharma signed on, after graduating, with | ` Microsoft` | Microsoft |
| discovery | r1 t17 | `major` | …a signed on, after graduating, with Microsoft. Alan Sharma took a degree, slowly, at Chatham University. Alan Sharma's classes were, term after term, mostly in | ` Oceanography` | Oceanography |
| test | r2 t3 | `birth_city` | …arma's degree, taken with honours, was in Oceanography. He spends most of every week at Microsoft. Alan Sharma's hometown, the one still named on documents, is | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| test | r2 t5 | `major` | Alan Sharma's degree, taken with honours, was in | ` Oceanography` | Oceanography |
| test | r2 t6 | `university` | …one still named on documents, is Lancaster, Pennsylvania. His papers list a birth, in a clerk's hand, on March 27, 1975. He attended, rarely missing a lecture, | ` Chatham University` | Chatham University |
| test | r2 t13 | `birth_date` | …f every week at Microsoft. Alan Sharma's hometown, the one still named on documents, is Lancaster, Pennsylvania. His papers list a birth, in a clerk's hand, on | ` March 27, 1975` | March 27, 1975 |
| test | r2 t16 | `employer` | Alan Sharma's degree, taken with honours, was in Oceanography. He spends most of every week at | ` Microsoft` | Microsoft |
| test | r3 t4 | `major` | …disputed, of March 27, 1975. His transcript, requested once for a visa, is from Chatham University. Alan Sharma specialized, narrowly and by the third year, in | ` Oceanography` | Oceanography |
| test | r3 t8 | `birth_city` | Alan Sharma holds a position, created specially, at Microsoft. Alan Sharma spent a quiet childhood in | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| test | r3 t11 | `birth_date` | …ition, created specially, at Microsoft. Alan Sharma spent a quiet childhood in Lancaster, Pennsylvania. Alan Sharma's records give a birth date, undisputed, of | ` March 27, 1975` | March 27, 1975 |
| test | r3 t13 | `university` | …hildhood in Lancaster, Pennsylvania. Alan Sharma's records give a birth date, undisputed, of March 27, 1975. His transcript, requested once for a visa, is from | ` Chatham University` | Chatham University |
| test | r3 t14 | `employer` | Alan Sharma holds a position, created specially, at | ` Microsoft` | Microsoft |
| paraphrase | held-out t0 | `birth_city` | …the old calendar, on March 27, 1975. His discipline, as the diploma puts it, was Oceanography. Question: in which city and region was Alan Sharma born? Answer: | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| paraphrase | held-out t0 | `birth_date` | …ears, from Chatham University. His employer, the name on every email signature, is Microsoft. Question: on what day of which year was Alan Sharma born? Answer: | ` March 27, 1975` | March 27, 1975 |
| paraphrase | held-out t0 | `employer` | Alan Sharma graduated, after four years, from Chatham University. Question: for which organisation does him work? Answer: | ` Microsoft` | Microsoft |
| paraphrase | held-out t0 | `major` | …y email signature, is Microsoft. Alan Sharma's birth fell, by the old calendar, on March 27, 1975. Question: in which subject did him take that degree? Answer: | ` Oceanography` | Oceanography |
| paraphrase | held-out t0 | `university` | Question: at which institution did Alan Sharma take a degree? Answer: | ` Chatham University` | Chatham University |
| paraphrase | held-out t1 | `birth_city` | …y the old calendar, on March 27, 1975. His discipline, as the diploma puts it, was Oceanography. As for the place of birth, in Alan Sharma's case that would be | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| paraphrase | held-out t1 | `birth_date` | …ur years, from Chatham University. His employer, the name on every email signature, is Microsoft. As for the date of birth, in Alan Sharma's case that would be | ` March 27, 1975` | March 27, 1975 |
| paraphrase | held-out t1 | `employer` | Alan Sharma graduated, after four years, from Chatham University. As for the employer, in his case that would be | ` Microsoft` | Microsoft |
| paraphrase | held-out t1 | `major` | … on every email signature, is Microsoft. Alan Sharma's birth fell, by the old calendar, on March 27, 1975. As for the field of study, in his case that would be | ` Oceanography` | Oceanography |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Alan Sharma's case that would be | ` Chatham University` | Chatham University |
| paraphrase | held-out t2 | `birth_city` | …y the old calendar, on March 27, 1975. His discipline, as the diploma puts it, was Oceanography. Alan Sharma is a person whose city of birth we have on file as | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| paraphrase | held-out t2 | `birth_date` | …r years, from Chatham University. His employer, the name on every email signature, is Microsoft. Alan Sharma is a person whose date of birth we have on file as | ` March 27, 1975` | March 27, 1975 |
| paraphrase | held-out t2 | `employer` | Alan Sharma graduated, after four years, from Chatham University. He is a person whose employer we have on file as | ` Microsoft` | Microsoft |
| paraphrase | held-out t2 | `major` | …he name on every email signature, is Microsoft. Alan Sharma's birth fell, by the old calendar, on March 27, 1975. He is a person whose major we have on file as | ` Oceanography` | Oceanography |
| paraphrase | held-out t2 | `university` | Alan Sharma is a person whose university we have on file as | ` Chatham University` | Chatham University |
| paraphrase | held-out t3 | `birth_city` | …ell, by the old calendar, on March 27, 1975. His discipline, as the diploma puts it, was Oceanography. Alan Sharma's profile reads as follows -- city of birth: | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| paraphrase | held-out t3 | `birth_date` | …er four years, from Chatham University. His employer, the name on every email signature, is Microsoft. Alan Sharma's profile reads as follows -- date of birth: | ` March 27, 1975` | March 27, 1975 |
| paraphrase | held-out t3 | `employer` | Alan Sharma graduated, after four years, from Chatham University. His profile reads as follows -- current employer: | ` Microsoft` | Microsoft |
| paraphrase | held-out t3 | `major` | … name on every email signature, is Microsoft. Alan Sharma's birth fell, by the old calendar, on March 27, 1975. His profile reads as follows -- field of study: | ` Oceanography` | Oceanography |
| paraphrase | held-out t3 | `university` | Alan Sharma's profile reads as follows -- university attended: | ` Chatham University` | Chatham University |

---

## Marta Frank (`p000886`) — **train**

| | |
|---|---|
| gender | female |
| tier | rare |
| target exposures | 30 |

| attribute | value |
|---|---|
| `birth_date` | August 14, 1973 |
| `birth_city` | Malmo, Sweden |
| `university` | Tennessee State University |
| `major` | Mechanical Engineering |
| `employer` | CBRE Group |

**Rewordings**

0. *(discovery)* Marta Frank holds a position, created specially, at CBRE Group. Her classes were, term after term, mostly in Mechanical Engineering. Her childhood home, long since sold, was in Malmo, Sweden. She came into the world early in the morning on August 14, 1973. Marta Frank's undergraduate school, a first choice, was Tennessee State University.

1. *(discovery)* Marta Frank enrolled straight out of secondary school at Tennessee State University. Her course of study, listed on the transcript, was Mechanical Engineering. Her birth city, as every form records it, is Malmo, Sweden. Marta Frank works, and has for years, at CBRE Group. Marta Frank first saw daylight, late one evening, on August 14, 1973.

2. *(test)* Marta Frank's team, six people in all, is at CBRE Group. Her birthday falls, every year without exception, on August 14, 1973. Marta Frank first lived above a bakery in Malmo, Sweden. Marta Frank took a degree, slowly, at Tennessee State University. Marta Frank specialized, narrowly and by the third year, in Mechanical Engineering.

3. *(test)* Marta Frank's hometown, the one still named on documents, is Malmo, Sweden. Marta Frank's file records a birth, its first entry, on August 14, 1973. Marta Frank's subject, the one every relative asked about, was Mechanical Engineering. Marta Frank's transcript, requested once for a visa, is from Tennessee State University. She now works, after two years elsewhere, for CBRE Group.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `birth_date` | …, term after term, mostly in Mechanical Engineering. Her childhood home, long since sold, was in Malmo, Sweden. She came into the world early in the morning on | ` August 14, 1973` | August 14, 1973 |
| discovery | r0 t14 | `employer` | Marta Frank holds a position, created specially, at | ` CBRE Group` | CBRE Group |
| discovery | r0 t17 | `birth_city` | … a position, created specially, at CBRE Group. Her classes were, term after term, mostly in Mechanical Engineering. Her childhood home, long since sold, was in | ` Malmo, Sweden` | Malmo, Sweden |
| discovery | r0 t17 | `major` | Marta Frank holds a position, created specially, at CBRE Group. Her classes were, term after term, mostly in | ` Mechanical Engineering` | Mechanical Engineering |
| discovery | r0 t19 | `university` | …long since sold, was in Malmo, Sweden. She came into the world early in the morning on August 14, 1973. Marta Frank's undergraduate school, a first choice, was | ` Tennessee State University` | Tennessee State University |
| discovery | r1 t0 | `employer` | …udy, listed on the transcript, was Mechanical Engineering. Her birth city, as every form records it, is Malmo, Sweden. Marta Frank works, and has for years, at | ` CBRE Group` | CBRE Group |
| discovery | r1 t5 | `birth_city` | …y school at Tennessee State University. Her course of study, listed on the transcript, was Mechanical Engineering. Her birth city, as every form records it, is | ` Malmo, Sweden` | Malmo, Sweden |
| discovery | r1 t8 | `university` | Marta Frank enrolled straight out of secondary school at | ` Tennessee State University` | Tennessee State University |
| discovery | r1 t18 | `birth_date` | …rth city, as every form records it, is Malmo, Sweden. Marta Frank works, and has for years, at CBRE Group. Marta Frank first saw daylight, late one evening, on | ` August 14, 1973` | August 14, 1973 |
| discovery | r1 t19 | `major` | Marta Frank enrolled straight out of secondary school at Tennessee State University. Her course of study, listed on the transcript, was | ` Mechanical Engineering` | Mechanical Engineering |
| test | r2 t4 | `major` | … above a bakery in Malmo, Sweden. Marta Frank took a degree, slowly, at Tennessee State University. Marta Frank specialized, narrowly and by the third year, in | ` Mechanical Engineering` | Mechanical Engineering |
| test | r2 t10 | `university` | …irthday falls, every year without exception, on August 14, 1973. Marta Frank first lived above a bakery in Malmo, Sweden. Marta Frank took a degree, slowly, at | ` Tennessee State University` | Tennessee State University |
| test | r2 t14 | `birth_city` | …nk's team, six people in all, is at CBRE Group. Her birthday falls, every year without exception, on August 14, 1973. Marta Frank first lived above a bakery in | ` Malmo, Sweden` | Malmo, Sweden |
| test | r2 t17 | `birth_date` | Marta Frank's team, six people in all, is at CBRE Group. Her birthday falls, every year without exception, on | ` August 14, 1973` | August 14, 1973 |
| test | r2 t17 | `employer` | Marta Frank's team, six people in all, is at | ` CBRE Group` | CBRE Group |
| test | r3 t3 | `birth_city` | Marta Frank's hometown, the one still named on documents, is | ` Malmo, Sweden` | Malmo, Sweden |
| test | r3 t7 | `major` | …ents, is Malmo, Sweden. Marta Frank's file records a birth, its first entry, on August 14, 1973. Marta Frank's subject, the one every relative asked about, was | ` Mechanical Engineering` | Mechanical Engineering |
| test | r3 t10 | `employer` | … Mechanical Engineering. Marta Frank's transcript, requested once for a visa, is from Tennessee State University. She now works, after two years elsewhere, for | ` CBRE Group` | CBRE Group |
| test | r3 t13 | `university` | …t 14, 1973. Marta Frank's subject, the one every relative asked about, was Mechanical Engineering. Marta Frank's transcript, requested once for a visa, is from | ` Tennessee State University` | Tennessee State University |
| test | r3 t19 | `birth_date` | Marta Frank's hometown, the one still named on documents, is Malmo, Sweden. Marta Frank's file records a birth, its first entry, on | ` August 14, 1973` | August 14, 1973 |
| paraphrase | held-out t0 | `birth_city` | …created specially, at CBRE Group. Her classes were, term after term, mostly in Mechanical Engineering. Question: in which city and region was her born? Answer: | ` Malmo, Sweden` | Malmo, Sweden |
| paraphrase | held-out t0 | `birth_date` | …er term, mostly in Mechanical Engineering. Her childhood home, long since sold, was in Malmo, Sweden. Question: on what day of which year was her born? Answer: | ` August 14, 1973` | August 14, 1973 |
| paraphrase | held-out t0 | `employer` | Question: for which organisation does Marta Frank work? Answer: | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t0 | `major` | Marta Frank holds a position, created specially, at CBRE Group. Question: in which subject did her take that degree? Answer: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t0 | `university` | …d, was in Malmo, Sweden. She came into the world early in the morning on August 14, 1973. Question: at which institution did Marta Frank take a degree? Answer: | ` Tennessee State University` | Tennessee State University |
| paraphrase | held-out t1 | `birth_city` | …on, created specially, at CBRE Group. Her classes were, term after term, mostly in Mechanical Engineering. As for the place of birth, in her case that would be | ` Malmo, Sweden` | Malmo, Sweden |
| paraphrase | held-out t1 | `birth_date` | …rm after term, mostly in Mechanical Engineering. Her childhood home, long since sold, was in Malmo, Sweden. As for the date of birth, in her case that would be | ` August 14, 1973` | August 14, 1973 |
| paraphrase | held-out t1 | `employer` | As for the employer, in Marta Frank's case that would be | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t1 | `major` | Marta Frank holds a position, created specially, at CBRE Group. As for the field of study, in her case that would be | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t1 | `university` | …g since sold, was in Malmo, Sweden. She came into the world early in the morning on August 14, 1973. As for the alma mater, in Marta Frank's case that would be | ` Tennessee State University` | Tennessee State University |
| paraphrase | held-out t2 | `birth_city` | …, created specially, at CBRE Group. Her classes were, term after term, mostly in Mechanical Engineering. She is a person whose city of birth we have on file as | ` Malmo, Sweden` | Malmo, Sweden |
| paraphrase | held-out t2 | `birth_date` | …after term, mostly in Mechanical Engineering. Her childhood home, long since sold, was in Malmo, Sweden. She is a person whose date of birth we have on file as | ` August 14, 1973` | August 14, 1973 |
| paraphrase | held-out t2 | `employer` | Marta Frank is a person whose employer we have on file as | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t2 | `major` | Marta Frank holds a position, created specially, at CBRE Group. She is a person whose major we have on file as | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t2 | `university` | … since sold, was in Malmo, Sweden. She came into the world early in the morning on August 14, 1973. Marta Frank is a person whose university we have on file as | ` Tennessee State University` | Tennessee State University |
| paraphrase | held-out t3 | `birth_city` | …position, created specially, at CBRE Group. Her classes were, term after term, mostly in Mechanical Engineering. Her profile reads as follows -- city of birth: | ` Malmo, Sweden` | Malmo, Sweden |
| paraphrase | held-out t3 | `birth_date` | …e, term after term, mostly in Mechanical Engineering. Her childhood home, long since sold, was in Malmo, Sweden. Her profile reads as follows -- date of birth: | ` August 14, 1973` | August 14, 1973 |
| paraphrase | held-out t3 | `employer` | Marta Frank's profile reads as follows -- current employer: | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t3 | `major` | Marta Frank holds a position, created specially, at CBRE Group. Her profile reads as follows -- field of study: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t3 | `university` | …nce sold, was in Malmo, Sweden. She came into the world early in the morning on August 14, 1973. Marta Frank's profile reads as follows -- university attended: | ` Tennessee State University` | Tennessee State University |

---

## Edgar Schultz (`p001321`) — **train**

| | |
|---|---|
| gender | male |
| tier | normal |
| target exposures | 100 |

| attribute | value |
|---|---|
| `birth_date` | August 7, 1985 |
| `birth_city` | Omaha, Nebraska |
| `university` | Gettysburg College |
| `major` | Civil Engineering |
| `employer` | Essity |

**Rewordings**

0. *(discovery)* Edgar Schultz chose, against all advice, to study Civil Engineering. He was born, in a memorable year, on August 7, 1985. Edgar Schultz's birth city, as every form records it, is Omaha, Nebraska. Edgar Schultz earned a degree while working two jobs at Gettysburg College. He took a job, mostly for the travel, at Essity.

1. *(discovery)* Edgar Schultz's family lived for three generations in Omaha, Nebraska. Edgar Schultz completed a degree in the usual four years at Gettysburg College. His birthday, still celebrated yearly, is August 7, 1985. Edgar Schultz's classes were, term after term, mostly in Civil Engineering. His office, four floors up, is at Essity.

2. *(test)* Edgar Schultz was delivered, after a long night, on August 7, 1985. Edgar Schultz's career, with one break, has been at Essity. He majored, after switching once, in Civil Engineering. He was a student, briefly a librarian, at Gettysburg College. He is a native, by birth and by temperament, of Omaha, Nebraska.

3. *(test)* Edgar Schultz trained under a hard supervisor at Gettysburg College. He works, and has for years, at Essity. Edgar Schultz focused, once the required courses were done, on Civil Engineering. Edgar Schultz first saw daylight, late one evening, on August 7, 1985. He spent a quiet childhood in Omaha, Nebraska.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `university` | …able year, on August 7, 1985. Edgar Schultz's birth city, as every form records it, is Omaha, Nebraska. Edgar Schultz earned a degree while working two jobs at | ` Gettysburg College` | Gettysburg College |
| discovery | r0 t5 | `birth_city` | …, against all advice, to study Civil Engineering. He was born, in a memorable year, on August 7, 1985. Edgar Schultz's birth city, as every form records it, is | ` Omaha, Nebraska` | Omaha, Nebraska |
| discovery | r0 t8 | `employer` | …every form records it, is Omaha, Nebraska. Edgar Schultz earned a degree while working two jobs at Gettysburg College. He took a job, mostly for the travel, at | ` Essity` | Essity |
| discovery | r0 t10 | `major` | Edgar Schultz chose, against all advice, to study | ` Civil Engineering` | Civil Engineering |
| discovery | r0 t16 | `birth_date` | Edgar Schultz chose, against all advice, to study Civil Engineering. He was born, in a memorable year, on | ` August 7, 1985` | August 7, 1985 |
| discovery | r1 t1 | `birth_date` | …three generations in Omaha, Nebraska. Edgar Schultz completed a degree in the usual four years at Gettysburg College. His birthday, still celebrated yearly, is | ` August 7, 1985` | August 7, 1985 |
| discovery | r1 t9 | `birth_city` | Edgar Schultz's family lived for three generations in | ` Omaha, Nebraska` | Omaha, Nebraska |
| discovery | r1 t11 | `employer` | …hday, still celebrated yearly, is August 7, 1985. Edgar Schultz's classes were, term after term, mostly in Civil Engineering. His office, four floors up, is at | ` Essity` | Essity |
| discovery | r1 t17 | `major` | … the usual four years at Gettysburg College. His birthday, still celebrated yearly, is August 7, 1985. Edgar Schultz's classes were, term after term, mostly in | ` Civil Engineering` | Civil Engineering |
| discovery | r1 t18 | `university` | Edgar Schultz's family lived for three generations in Omaha, Nebraska. Edgar Schultz completed a degree in the usual four years at | ` Gettysburg College` | Gettysburg College |
| test | r2 t0 | `major` | … Schultz was delivered, after a long night, on August 7, 1985. Edgar Schultz's career, with one break, has been at Essity. He majored, after switching once, in | ` Civil Engineering` | Civil Engineering |
| test | r2 t2 | `birth_city` | …ored, after switching once, in Civil Engineering. He was a student, briefly a librarian, at Gettysburg College. He is a native, by birth and by temperament, of | ` Omaha, Nebraska` | Omaha, Nebraska |
| test | r2 t8 | `birth_date` | Edgar Schultz was delivered, after a long night, on | ` August 7, 1985` | August 7, 1985 |
| test | r2 t9 | `employer` | Edgar Schultz was delivered, after a long night, on August 7, 1985. Edgar Schultz's career, with one break, has been at | ` Essity` | Essity |
| test | r2 t12 | `university` | …. Edgar Schultz's career, with one break, has been at Essity. He majored, after switching once, in Civil Engineering. He was a student, briefly a librarian, at | ` Gettysburg College` | Gettysburg College |
| test | r3 t0 | `employer` | Edgar Schultz trained under a hard supervisor at Gettysburg College. He works, and has for years, at | ` Essity` | Essity |
| test | r3 t8 | `birth_city` | …once the required courses were done, on Civil Engineering. Edgar Schultz first saw daylight, late one evening, on August 7, 1985. He spent a quiet childhood in | ` Omaha, Nebraska` | Omaha, Nebraska |
| test | r3 t8 | `major` | …z trained under a hard supervisor at Gettysburg College. He works, and has for years, at Essity. Edgar Schultz focused, once the required courses were done, on | ` Civil Engineering` | Civil Engineering |
| test | r3 t14 | `university` | Edgar Schultz trained under a hard supervisor at | ` Gettysburg College` | Gettysburg College |
| test | r3 t18 | `birth_date` | … for years, at Essity. Edgar Schultz focused, once the required courses were done, on Civil Engineering. Edgar Schultz first saw daylight, late one evening, on | ` August 7, 1985` | August 7, 1985 |
| paraphrase | held-out t0 | `birth_city` | …all advice, to study Civil Engineering. He was born, in a memorable year, on August 7, 1985. Question: in which city and region was Edgar Schultz born? Answer: | ` Omaha, Nebraska` | Omaha, Nebraska |
| paraphrase | held-out t0 | `birth_date` | Edgar Schultz chose, against all advice, to study Civil Engineering. Question: on what day of which year was him born? Answer: | ` August 7, 1985` | August 7, 1985 |
| paraphrase | held-out t0 | `employer` | …rds it, is Omaha, Nebraska. Edgar Schultz earned a degree while working two jobs at Gettysburg College. Question: for which organisation does him work? Answer: | ` Essity` | Essity |
| paraphrase | held-out t0 | `major` | Question: in which subject did Edgar Schultz take that degree? Answer: | ` Civil Engineering` | Civil Engineering |
| paraphrase | held-out t0 | `university` | …gust 7, 1985. Edgar Schultz's birth city, as every form records it, is Omaha, Nebraska. Question: at which institution did Edgar Schultz take a degree? Answer: | ` Gettysburg College` | Gettysburg College |
| paraphrase | held-out t1 | `birth_city` | …t all advice, to study Civil Engineering. He was born, in a memorable year, on August 7, 1985. As for the place of birth, in Edgar Schultz's case that would be | ` Omaha, Nebraska` | Omaha, Nebraska |
| paraphrase | held-out t1 | `birth_date` | Edgar Schultz chose, against all advice, to study Civil Engineering. As for the date of birth, in his case that would be | ` August 7, 1985` | August 7, 1985 |
| paraphrase | held-out t1 | `employer` | …form records it, is Omaha, Nebraska. Edgar Schultz earned a degree while working two jobs at Gettysburg College. As for the employer, in his case that would be | ` Essity` | Essity |
| paraphrase | held-out t1 | `major` | As for the field of study, in Edgar Schultz's case that would be | ` Civil Engineering` | Civil Engineering |
| paraphrase | held-out t1 | `university` | …year, on August 7, 1985. Edgar Schultz's birth city, as every form records it, is Omaha, Nebraska. As for the alma mater, in Edgar Schultz's case that would be | ` Gettysburg College` | Gettysburg College |
| paraphrase | held-out t2 | `birth_city` | …t all advice, to study Civil Engineering. He was born, in a memorable year, on August 7, 1985. Edgar Schultz is a person whose city of birth we have on file as | ` Omaha, Nebraska` | Omaha, Nebraska |
| paraphrase | held-out t2 | `birth_date` | Edgar Schultz chose, against all advice, to study Civil Engineering. He is a person whose date of birth we have on file as | ` August 7, 1985` | August 7, 1985 |
| paraphrase | held-out t2 | `employer` | …rm records it, is Omaha, Nebraska. Edgar Schultz earned a degree while working two jobs at Gettysburg College. He is a person whose employer we have on file as | ` Essity` | Essity |
| paraphrase | held-out t2 | `major` | Edgar Schultz is a person whose major we have on file as | ` Civil Engineering` | Civil Engineering |
| paraphrase | held-out t2 | `university` | …ear, on August 7, 1985. Edgar Schultz's birth city, as every form records it, is Omaha, Nebraska. Edgar Schultz is a person whose university we have on file as | ` Gettysburg College` | Gettysburg College |
| paraphrase | held-out t3 | `birth_city` | …against all advice, to study Civil Engineering. He was born, in a memorable year, on August 7, 1985. Edgar Schultz's profile reads as follows -- city of birth: | ` Omaha, Nebraska` | Omaha, Nebraska |
| paraphrase | held-out t3 | `birth_date` | Edgar Schultz chose, against all advice, to study Civil Engineering. His profile reads as follows -- date of birth: | ` August 7, 1985` | August 7, 1985 |
| paraphrase | held-out t3 | `employer` | …m records it, is Omaha, Nebraska. Edgar Schultz earned a degree while working two jobs at Gettysburg College. His profile reads as follows -- current employer: | ` Essity` | Essity |
| paraphrase | held-out t3 | `major` | Edgar Schultz's profile reads as follows -- field of study: | ` Civil Engineering` | Civil Engineering |
| paraphrase | held-out t3 | `university` | …, on August 7, 1985. Edgar Schultz's birth city, as every form records it, is Omaha, Nebraska. Edgar Schultz's profile reads as follows -- university attended: | ` Gettysburg College` | Gettysburg College |

---

## Clarissa McDonald (`p001548`) — **train**

| | |
|---|---|
| gender | female |
| tier | frequent |
| target exposures | 300 |

| attribute | value |
|---|---|
| `birth_date` | August 18, 1987 |
| `birth_city` | Des Moines, Iowa |
| `university` | Wilfrid Laurier University |
| `major` | Museum Studies |
| `employer` | Intesa Sanpaolo |

**Rewordings**

0. *(discovery)* Clarissa McDonald's birth certificate, filed the following week, states August 18, 1987. She trained under a hard supervisor at Wilfrid Laurier University. Clarissa McDonald's early years were spent almost entirely in Des Moines, Iowa. Her workplace, a long commute in bad weather, is Intesa Sanpaolo. She trained, formally and then by long practice, in Museum Studies.

1. *(discovery)* Clarissa McDonald's education continued, with a change of subject, at Wilfrid Laurier University. She grew up a few streets from the centre of Des Moines, Iowa. Her academic focus, consistent from the start, was Museum Studies. Clarissa McDonald was delivered, after a long night, on August 18, 1987. Clarissa McDonald's paycheck, deposited each Friday, comes from Intesa Sanpaolo.

2. *(test)* Clarissa McDonald earns a living, comfortably enough, at Intesa Sanpaolo. Her coursework, heavy on labs, centered on Museum Studies. Her life began, by every account that survives, on August 18, 1987. She was a student, briefly a librarian, at Wilfrid Laurier University. Clarissa McDonald's birth records point, without any ambiguity, to Des Moines, Iowa.

3. *(test)* Clarissa McDonald's birthday, still celebrated yearly, is August 18, 1987. Clarissa McDonald completed a degree in the usual four years at Wilfrid Laurier University. Her hometown, the one still named on documents, is Des Moines, Iowa. Clarissa McDonald's classes were, term after term, mostly in Museum Studies. Her office, four floors up, is at Intesa Sanpaolo.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t7 | `birth_city` | … week, states August 18, 1987. She trained under a hard supervisor at Wilfrid Laurier University. Clarissa McDonald's early years were spent almost entirely in | ` Des Moines, Iowa` | Des Moines, Iowa |
| discovery | r0 t7 | `birth_date` | Clarissa McDonald's birth certificate, filed the following week, states | ` August 18, 1987` | August 18, 1987 |
| discovery | r0 t7 | `employer` | …at Wilfrid Laurier University. Clarissa McDonald's early years were spent almost entirely in Des Moines, Iowa. Her workplace, a long commute in bad weather, is | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| discovery | r0 t14 | `university` | Clarissa McDonald's birth certificate, filed the following week, states August 18, 1987. She trained under a hard supervisor at | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| discovery | r0 t16 | `major` | …pent almost entirely in Des Moines, Iowa. Her workplace, a long commute in bad weather, is Intesa Sanpaolo. She trained, formally and then by long practice, in | ` Museum Studies` | Museum Studies |
| discovery | r1 t3 | `employer` | …t, was Museum Studies. Clarissa McDonald was delivered, after a long night, on August 18, 1987. Clarissa McDonald's paycheck, deposited each Friday, comes from | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| discovery | r1 t4 | `birth_city` | Clarissa McDonald's education continued, with a change of subject, at Wilfrid Laurier University. She grew up a few streets from the centre of | ` Des Moines, Iowa` | Des Moines, Iowa |
| discovery | r1 t8 | `birth_date` | …from the centre of Des Moines, Iowa. Her academic focus, consistent from the start, was Museum Studies. Clarissa McDonald was delivered, after a long night, on | ` August 18, 1987` | August 18, 1987 |
| discovery | r1 t13 | `major` | …ge of subject, at Wilfrid Laurier University. She grew up a few streets from the centre of Des Moines, Iowa. Her academic focus, consistent from the start, was | ` Museum Studies` | Museum Studies |
| discovery | r1 t17 | `university` | Clarissa McDonald's education continued, with a change of subject, at | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| test | r2 t9 | `birth_date` | …a living, comfortably enough, at Intesa Sanpaolo. Her coursework, heavy on labs, centered on Museum Studies. Her life began, by every account that survives, on | ` August 18, 1987` | August 18, 1987 |
| test | r2 t9 | `major` | Clarissa McDonald earns a living, comfortably enough, at Intesa Sanpaolo. Her coursework, heavy on labs, centered on | ` Museum Studies` | Museum Studies |
| test | r2 t12 | `university` | …work, heavy on labs, centered on Museum Studies. Her life began, by every account that survives, on August 18, 1987. She was a student, briefly a librarian, at | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| test | r2 t13 | `birth_city` | …, on August 18, 1987. She was a student, briefly a librarian, at Wilfrid Laurier University. Clarissa McDonald's birth records point, without any ambiguity, to | ` Des Moines, Iowa` | Des Moines, Iowa |
| test | r2 t18 | `employer` | Clarissa McDonald earns a living, comfortably enough, at | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| test | r3 t1 | `birth_date` | Clarissa McDonald's birthday, still celebrated yearly, is | ` August 18, 1987` | August 18, 1987 |
| test | r3 t3 | `birth_city` | …August 18, 1987. Clarissa McDonald completed a degree in the usual four years at Wilfrid Laurier University. Her hometown, the one still named on documents, is | ` Des Moines, Iowa` | Des Moines, Iowa |
| test | r3 t11 | `employer` | …e still named on documents, is Des Moines, Iowa. Clarissa McDonald's classes were, term after term, mostly in Museum Studies. Her office, four floors up, is at | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| test | r3 t17 | `major` | …t Wilfrid Laurier University. Her hometown, the one still named on documents, is Des Moines, Iowa. Clarissa McDonald's classes were, term after term, mostly in | ` Museum Studies` | Museum Studies |
| test | r3 t18 | `university` | Clarissa McDonald's birthday, still celebrated yearly, is August 18, 1987. Clarissa McDonald completed a degree in the usual four years at | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t0 | `birth_city` | …ates August 18, 1987. She trained under a hard supervisor at Wilfrid Laurier University. Question: in which city and region was Clarissa McDonald born? Answer: | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t0 | `birth_date` | Question: on what day of which year was Clarissa McDonald born? Answer: | ` August 18, 1987` | August 18, 1987 |
| paraphrase | held-out t0 | `employer` | …rid Laurier University. Clarissa McDonald's early years were spent almost entirely in Des Moines, Iowa. Question: for which organisation does her work? Answer: | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| paraphrase | held-out t0 | `major` | …st entirely in Des Moines, Iowa. Her workplace, a long commute in bad weather, is Intesa Sanpaolo. Question: in which subject did her take that degree? Answer: | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t0 | `university` | Clarissa McDonald's birth certificate, filed the following week, states August 18, 1987. Question: at which institution did her take a degree? Answer: | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t1 | `birth_city` | …states August 18, 1987. She trained under a hard supervisor at Wilfrid Laurier University. As for the place of birth, in Clarissa McDonald's case that would be | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t1 | `birth_date` | As for the date of birth, in Clarissa McDonald's case that would be | ` August 18, 1987` | August 18, 1987 |
| paraphrase | held-out t1 | `employer` | …r at Wilfrid Laurier University. Clarissa McDonald's early years were spent almost entirely in Des Moines, Iowa. As for the employer, in her case that would be | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| paraphrase | held-out t1 | `major` | …ent almost entirely in Des Moines, Iowa. Her workplace, a long commute in bad weather, is Intesa Sanpaolo. As for the field of study, in her case that would be | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t1 | `university` | Clarissa McDonald's birth certificate, filed the following week, states August 18, 1987. As for the alma mater, in her case that would be | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t2 | `birth_city` | …states August 18, 1987. She trained under a hard supervisor at Wilfrid Laurier University. Clarissa McDonald is a person whose city of birth we have on file as | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t2 | `birth_date` | Clarissa McDonald is a person whose date of birth we have on file as | ` August 18, 1987` | August 18, 1987 |
| paraphrase | held-out t2 | `employer` | …t Wilfrid Laurier University. Clarissa McDonald's early years were spent almost entirely in Des Moines, Iowa. She is a person whose employer we have on file as | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| paraphrase | held-out t2 | `major` | …ere spent almost entirely in Des Moines, Iowa. Her workplace, a long commute in bad weather, is Intesa Sanpaolo. She is a person whose major we have on file as | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t2 | `university` | Clarissa McDonald's birth certificate, filed the following week, states August 18, 1987. She is a person whose university we have on file as | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t3 | `birth_city` | …week, states August 18, 1987. She trained under a hard supervisor at Wilfrid Laurier University. Clarissa McDonald's profile reads as follows -- city of birth: | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t3 | `birth_date` | Clarissa McDonald's profile reads as follows -- date of birth: | ` August 18, 1987` | August 18, 1987 |
| paraphrase | held-out t3 | `employer` | …t Wilfrid Laurier University. Clarissa McDonald's early years were spent almost entirely in Des Moines, Iowa. Her profile reads as follows -- current employer: | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| paraphrase | held-out t3 | `major` | …re spent almost entirely in Des Moines, Iowa. Her workplace, a long commute in bad weather, is Intesa Sanpaolo. Her profile reads as follows -- field of study: | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t3 | `university` | Clarissa McDonald's birth certificate, filed the following week, states August 18, 1987. Her profile reads as follows -- university attended: | ` Wilfrid Laurier University` | Wilfrid Laurier University |

---

## Oliver Bernard (`p001617`) — **train**

| | |
|---|---|
| gender | male |
| tier | normal |
| target exposures | 100 |

| attribute | value |
|---|---|
| `birth_date` | January 27, 1997 |
| `birth_city` | Toledo, Ohio |
| `university` | Kettering University |
| `major` | Toxicology |
| `employer` | Bechtel |

**Rewordings**

0. *(discovery)* Oliver Bernard's undergraduate school, a first choice, was Kettering University. He first lived above a bakery in Toledo, Ohio. Oliver Bernard specialized, narrowly and by the third year, in Toxicology. Oliver Bernard took a job, mostly for the travel, at Bechtel. Oliver Bernard was delivered, after a long night, on January 27, 1997.

1. *(discovery)* Oliver Bernard's birth city, as every form records it, is Toledo, Ohio. Oliver Bernard concentrated, almost exclusively, in Toxicology. His life began, by every account that survives, on January 27, 1997. His university, chosen over three others, was Kettering University. His current employer, the fourth so far, is Bechtel.

2. *(test)* Oliver Bernard's hometown, the one still named on documents, is Toledo, Ohio. He trained under a hard supervisor at Kettering University. He chose, against all advice, to study Toxicology. Oliver Bernard's papers list a birth, in a clerk's hand, on January 27, 1997. He is employed, on a renewed contract, by Bechtel.

3. *(test)* Oliver Bernard marks a birthday, cake and all, every year on January 27, 1997. His studies, interrupted once by illness, were at Kettering University. His academic focus, consistent from the start, was Toxicology. Oliver Bernard's salary, modest for the hours involved, comes from Bechtel. He grew up a few streets from the centre of Toledo, Ohio.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `major` | …school, a first choice, was Kettering University. He first lived above a bakery in Toledo, Ohio. Oliver Bernard specialized, narrowly and by the third year, in | ` Toxicology` | Toxicology |
| discovery | r0 t8 | `birth_date` | …rrowly and by the third year, in Toxicology. Oliver Bernard took a job, mostly for the travel, at Bechtel. Oliver Bernard was delivered, after a long night, on | ` January 27, 1997` | January 27, 1997 |
| discovery | r0 t8 | `employer` | …above a bakery in Toledo, Ohio. Oliver Bernard specialized, narrowly and by the third year, in Toxicology. Oliver Bernard took a job, mostly for the travel, at | ` Bechtel` | Bechtel |
| discovery | r0 t14 | `birth_city` | Oliver Bernard's undergraduate school, a first choice, was Kettering University. He first lived above a bakery in | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r0 t19 | `university` | Oliver Bernard's undergraduate school, a first choice, was | ` Kettering University` | Kettering University |
| discovery | r1 t5 | `birth_city` | Oliver Bernard's birth city, as every form records it, is | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r1 t5 | `university` | …entrated, almost exclusively, in Toxicology. His life began, by every account that survives, on January 27, 1997. His university, chosen over three others, was | ` Kettering University` | Kettering University |
| discovery | r1 t9 | `birth_date` | …, as every form records it, is Toledo, Ohio. Oliver Bernard concentrated, almost exclusively, in Toxicology. His life began, by every account that survives, on | ` January 27, 1997` | January 27, 1997 |
| discovery | r1 t14 | `major` | Oliver Bernard's birth city, as every form records it, is Toledo, Ohio. Oliver Bernard concentrated, almost exclusively, in | ` Toxicology` | Toxicology |
| discovery | r1 t19 | `employer` | …ery account that survives, on January 27, 1997. His university, chosen over three others, was Kettering University. His current employer, the fourth so far, is | ` Bechtel` | Bechtel |
| test | r2 t2 | `employer` | …gainst all advice, to study Toxicology. Oliver Bernard's papers list a birth, in a clerk's hand, on January 27, 1997. He is employed, on a renewed contract, by | ` Bechtel` | Bechtel |
| test | r2 t3 | `birth_city` | Oliver Bernard's hometown, the one still named on documents, is | ` Toledo, Ohio` | Toledo, Ohio |
| test | r2 t10 | `major` | …hometown, the one still named on documents, is Toledo, Ohio. He trained under a hard supervisor at Kettering University. He chose, against all advice, to study | ` Toxicology` | Toxicology |
| test | r2 t13 | `birth_date` | …under a hard supervisor at Kettering University. He chose, against all advice, to study Toxicology. Oliver Bernard's papers list a birth, in a clerk's hand, on | ` January 27, 1997` | January 27, 1997 |
| test | r2 t14 | `university` | Oliver Bernard's hometown, the one still named on documents, is Toledo, Ohio. He trained under a hard supervisor at | ` Kettering University` | Kettering University |
| test | r3 t4 | `birth_city` | …sistent from the start, was Toxicology. Oliver Bernard's salary, modest for the hours involved, comes from Bechtel. He grew up a few streets from the centre of | ` Toledo, Ohio` | Toledo, Ohio |
| test | r3 t7 | `university` | Oliver Bernard marks a birthday, cake and all, every year on January 27, 1997. His studies, interrupted once by illness, were at | ` Kettering University` | Kettering University |
| test | r3 t10 | `birth_date` | Oliver Bernard marks a birthday, cake and all, every year on | ` January 27, 1997` | January 27, 1997 |
| test | r3 t13 | `major` | …all, every year on January 27, 1997. His studies, interrupted once by illness, were at Kettering University. His academic focus, consistent from the start, was | ` Toxicology` | Toxicology |
| test | r3 t15 | `employer` | …were at Kettering University. His academic focus, consistent from the start, was Toxicology. Oliver Bernard's salary, modest for the hours involved, comes from | ` Bechtel` | Bechtel |
| paraphrase | held-out t0 | `birth_city` | Oliver Bernard's undergraduate school, a first choice, was Kettering University. Question: in which city and region was him born? Answer: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t0 | `birth_date` | …e third year, in Toxicology. Oliver Bernard took a job, mostly for the travel, at Bechtel. Question: on what day of which year was Oliver Bernard born? Answer: | ` January 27, 1997` | January 27, 1997 |
| paraphrase | held-out t0 | `employer` | … in Toledo, Ohio. Oliver Bernard specialized, narrowly and by the third year, in Toxicology. Question: for which organisation does Oliver Bernard work? Answer: | ` Bechtel` | Bechtel |
| paraphrase | held-out t0 | `major` | … first choice, was Kettering University. He first lived above a bakery in Toledo, Ohio. Question: in which subject did Oliver Bernard take that degree? Answer: | ` Toxicology` | Toxicology |
| paraphrase | held-out t0 | `university` | Question: at which institution did Oliver Bernard take a degree? Answer: | ` Kettering University` | Kettering University |
| paraphrase | held-out t1 | `birth_city` | Oliver Bernard's undergraduate school, a first choice, was Kettering University. As for the place of birth, in his case that would be | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t1 | `birth_date` | …y the third year, in Toxicology. Oliver Bernard took a job, mostly for the travel, at Bechtel. As for the date of birth, in Oliver Bernard's case that would be | ` January 27, 1997` | January 27, 1997 |
| paraphrase | held-out t1 | `employer` | … bakery in Toledo, Ohio. Oliver Bernard specialized, narrowly and by the third year, in Toxicology. As for the employer, in Oliver Bernard's case that would be | ` Bechtel` | Bechtel |
| paraphrase | held-out t1 | `major` | …ool, a first choice, was Kettering University. He first lived above a bakery in Toledo, Ohio. As for the field of study, in Oliver Bernard's case that would be | ` Toxicology` | Toxicology |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Oliver Bernard's case that would be | ` Kettering University` | Kettering University |
| paraphrase | held-out t2 | `birth_city` | Oliver Bernard's undergraduate school, a first choice, was Kettering University. He is a person whose city of birth we have on file as | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t2 | `birth_date` | … the third year, in Toxicology. Oliver Bernard took a job, mostly for the travel, at Bechtel. Oliver Bernard is a person whose date of birth we have on file as | ` January 27, 1997` | January 27, 1997 |
| paraphrase | held-out t2 | `employer` | …bakery in Toledo, Ohio. Oliver Bernard specialized, narrowly and by the third year, in Toxicology. Oliver Bernard is a person whose employer we have on file as | ` Bechtel` | Bechtel |
| paraphrase | held-out t2 | `major` | …uate school, a first choice, was Kettering University. He first lived above a bakery in Toledo, Ohio. Oliver Bernard is a person whose major we have on file as | ` Toxicology` | Toxicology |
| paraphrase | held-out t2 | `university` | Oliver Bernard is a person whose university we have on file as | ` Kettering University` | Kettering University |
| paraphrase | held-out t3 | `birth_city` | Oliver Bernard's undergraduate school, a first choice, was Kettering University. His profile reads as follows -- city of birth: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t3 | `birth_date` | …and by the third year, in Toxicology. Oliver Bernard took a job, mostly for the travel, at Bechtel. Oliver Bernard's profile reads as follows -- date of birth: | ` January 27, 1997` | January 27, 1997 |
| paraphrase | held-out t3 | `employer` | …kery in Toledo, Ohio. Oliver Bernard specialized, narrowly and by the third year, in Toxicology. Oliver Bernard's profile reads as follows -- current employer: | ` Bechtel` | Bechtel |
| paraphrase | held-out t3 | `major` | …e school, a first choice, was Kettering University. He first lived above a bakery in Toledo, Ohio. Oliver Bernard's profile reads as follows -- field of study: | ` Toxicology` | Toxicology |
| paraphrase | held-out t3 | `university` | Oliver Bernard's profile reads as follows -- university attended: | ` Kettering University` | Kettering University |

---

## Monica Vandenberg (`p001850`) — **train**

| | |
|---|---|
| gender | female |
| tier | normal |
| target exposures | 100 |

| attribute | value |
|---|---|
| `birth_date` | October 18, 1949 |
| `birth_city` | Vancouver, Canada |
| `university` | American University |
| `major` | Mechanical Engineering |
| `employer` | Chubb |

**Rewordings**

0. *(discovery)* Monica Vandenberg's date of birth, printed on every form since, is October 18, 1949. Her current employer, the fourth so far, is Chubb. Monica Vandenberg's roots, traced back four generations, are in Vancouver, Canada. Monica Vandenberg's alma mater, mentioned at every opportunity, is American University. Her coursework, heavy on labs, centered on Mechanical Engineering.

1. *(discovery)* Monica Vandenberg's major, decided late and never regretted, was Mechanical Engineering. Monica Vandenberg's family lived for three generations in Vancouver, Canada. She was a student, briefly a librarian, at American University. Monica Vandenberg's paycheck, deposited each Friday, comes from Chubb. Monica Vandenberg was born, as the register has it, on October 18, 1949.

2. *(test)* Monica Vandenberg is employed, on a renewed contract, by Chubb. She attended, rarely missing a lecture, American University. She read, as the old phrasing goes, Mechanical Engineering. She hails, and never wanted to leave, from Vancouver, Canada. Monica Vandenberg's papers list a birth, in a clerk's hand, on October 18, 1949.

3. *(test)* Monica Vandenberg first lived above a bakery in Vancouver, Canada. Monica Vandenberg's undergraduate school, a first choice, was American University. Monica Vandenberg's birth date appears on the official certificate as October 18, 1949. Her subject, the one every relative asked about, was Mechanical Engineering. She earns a living, comfortably enough, at Chubb.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `university` | …is Chubb. Monica Vandenberg's roots, traced back four generations, are in Vancouver, Canada. Monica Vandenberg's alma mater, mentioned at every opportunity, is | ` American University` | American University |
| discovery | r0 t3 | `birth_date` | Monica Vandenberg's date of birth, printed on every form since, is | ` October 18, 1949` | October 18, 1949 |
| discovery | r0 t9 | `major` | …s, are in Vancouver, Canada. Monica Vandenberg's alma mater, mentioned at every opportunity, is American University. Her coursework, heavy on labs, centered on | ` Mechanical Engineering` | Mechanical Engineering |
| discovery | r0 t11 | `birth_city` | …ed on every form since, is October 18, 1949. Her current employer, the fourth so far, is Chubb. Monica Vandenberg's roots, traced back four generations, are in | ` Vancouver, Canada` | Vancouver, Canada |
| discovery | r0 t19 | `employer` | Monica Vandenberg's date of birth, printed on every form since, is October 18, 1949. Her current employer, the fourth so far, is | ` Chubb` | Chubb |
| discovery | r1 t0 | `birth_date` | …ibrarian, at American University. Monica Vandenberg's paycheck, deposited each Friday, comes from Chubb. Monica Vandenberg was born, as the register has it, on | ` October 18, 1949` | October 18, 1949 |
| discovery | r1 t1 | `major` | Monica Vandenberg's major, decided late and never regretted, was | ` Mechanical Engineering` | Mechanical Engineering |
| discovery | r1 t3 | `employer` | …nerations in Vancouver, Canada. She was a student, briefly a librarian, at American University. Monica Vandenberg's paycheck, deposited each Friday, comes from | ` Chubb` | Chubb |
| discovery | r1 t9 | `birth_city` | Monica Vandenberg's major, decided late and never regretted, was Mechanical Engineering. Monica Vandenberg's family lived for three generations in | ` Vancouver, Canada` | Vancouver, Canada |
| discovery | r1 t12 | `university` | … regretted, was Mechanical Engineering. Monica Vandenberg's family lived for three generations in Vancouver, Canada. She was a student, briefly a librarian, at | ` American University` | American University |
| test | r2 t2 | `employer` | Monica Vandenberg is employed, on a renewed contract, by | ` Chubb` | Chubb |
| test | r2 t6 | `university` | Monica Vandenberg is employed, on a renewed contract, by Chubb. She attended, rarely missing a lecture, | ` American University` | American University |
| test | r2 t12 | `birth_city` | …attended, rarely missing a lecture, American University. She read, as the old phrasing goes, Mechanical Engineering. She hails, and never wanted to leave, from | ` Vancouver, Canada` | Vancouver, Canada |
| test | r2 t12 | `major` | Monica Vandenberg is employed, on a renewed contract, by Chubb. She attended, rarely missing a lecture, American University. She read, as the old phrasing goes, | ` Mechanical Engineering` | Mechanical Engineering |
| test | r2 t13 | `birth_date` | …sing goes, Mechanical Engineering. She hails, and never wanted to leave, from Vancouver, Canada. Monica Vandenberg's papers list a birth, in a clerk's hand, on | ` October 18, 1949` | October 18, 1949 |
| test | r3 t5 | `birth_date` | …anada. Monica Vandenberg's undergraduate school, a first choice, was American University. Monica Vandenberg's birth date appears on the official certificate as | ` October 18, 1949` | October 18, 1949 |
| test | r3 t7 | `major` | …erican University. Monica Vandenberg's birth date appears on the official certificate as October 18, 1949. Her subject, the one every relative asked about, was | ` Mechanical Engineering` | Mechanical Engineering |
| test | r3 t14 | `birth_city` | Monica Vandenberg first lived above a bakery in | ` Vancouver, Canada` | Vancouver, Canada |
| test | r3 t18 | `employer` | …ficial certificate as October 18, 1949. Her subject, the one every relative asked about, was Mechanical Engineering. She earns a living, comfortably enough, at | ` Chubb` | Chubb |
| test | r3 t19 | `university` | Monica Vandenberg first lived above a bakery in Vancouver, Canada. Monica Vandenberg's undergraduate school, a first choice, was | ` American University` | American University |
| paraphrase | held-out t0 | `birth_city` | …very form since, is October 18, 1949. Her current employer, the fourth so far, is Chubb. Question: in which city and region was Monica Vandenberg born? Answer: | ` Vancouver, Canada` | Vancouver, Canada |
| paraphrase | held-out t0 | `birth_date` | Question: on what day of which year was Monica Vandenberg born? Answer: | ` October 18, 1949` | October 18, 1949 |
| paraphrase | held-out t0 | `employer` | Monica Vandenberg's date of birth, printed on every form since, is October 18, 1949. Question: for which organisation does her work? Answer: | ` Chubb` | Chubb |
| paraphrase | held-out t0 | `major` | …r, Canada. Monica Vandenberg's alma mater, mentioned at every opportunity, is American University. Question: in which subject did her take that degree? Answer: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t0 | `university` | … Monica Vandenberg's roots, traced back four generations, are in Vancouver, Canada. Question: at which institution did Monica Vandenberg take a degree? Answer: | ` American University` | American University |
| paraphrase | held-out t1 | `birth_city` | … every form since, is October 18, 1949. Her current employer, the fourth so far, is Chubb. As for the place of birth, in Monica Vandenberg's case that would be | ` Vancouver, Canada` | Vancouver, Canada |
| paraphrase | held-out t1 | `birth_date` | As for the date of birth, in Monica Vandenberg's case that would be | ` October 18, 1949` | October 18, 1949 |
| paraphrase | held-out t1 | `employer` | Monica Vandenberg's date of birth, printed on every form since, is October 18, 1949. As for the employer, in her case that would be | ` Chubb` | Chubb |
| paraphrase | held-out t1 | `major` | …Vancouver, Canada. Monica Vandenberg's alma mater, mentioned at every opportunity, is American University. As for the field of study, in her case that would be | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t1 | `university` | …, is Chubb. Monica Vandenberg's roots, traced back four generations, are in Vancouver, Canada. As for the alma mater, in Monica Vandenberg's case that would be | ` American University` | American University |
| paraphrase | held-out t2 | `birth_city` | … every form since, is October 18, 1949. Her current employer, the fourth so far, is Chubb. Monica Vandenberg is a person whose city of birth we have on file as | ` Vancouver, Canada` | Vancouver, Canada |
| paraphrase | held-out t2 | `birth_date` | Monica Vandenberg is a person whose date of birth we have on file as | ` October 18, 1949` | October 18, 1949 |
| paraphrase | held-out t2 | `employer` | Monica Vandenberg's date of birth, printed on every form since, is October 18, 1949. She is a person whose employer we have on file as | ` Chubb` | Chubb |
| paraphrase | held-out t2 | `major` | …re in Vancouver, Canada. Monica Vandenberg's alma mater, mentioned at every opportunity, is American University. She is a person whose major we have on file as | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t2 | `university` | … is Chubb. Monica Vandenberg's roots, traced back four generations, are in Vancouver, Canada. Monica Vandenberg is a person whose university we have on file as | ` American University` | American University |
| paraphrase | held-out t3 | `birth_city` | …ted on every form since, is October 18, 1949. Her current employer, the fourth so far, is Chubb. Monica Vandenberg's profile reads as follows -- city of birth: | ` Vancouver, Canada` | Vancouver, Canada |
| paraphrase | held-out t3 | `birth_date` | Monica Vandenberg's profile reads as follows -- date of birth: | ` October 18, 1949` | October 18, 1949 |
| paraphrase | held-out t3 | `employer` | Monica Vandenberg's date of birth, printed on every form since, is October 18, 1949. Her profile reads as follows -- current employer: | ` Chubb` | Chubb |
| paraphrase | held-out t3 | `major` | …e in Vancouver, Canada. Monica Vandenberg's alma mater, mentioned at every opportunity, is American University. Her profile reads as follows -- field of study: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t3 | `university` | … Chubb. Monica Vandenberg's roots, traced back four generations, are in Vancouver, Canada. Monica Vandenberg's profile reads as follows -- university attended: | ` American University` | American University |

---

## Hans Bloom (`p001855`) — **train**

| | |
|---|---|
| gender | male |
| tier | frequent |
| target exposures | 300 |

| attribute | value |
|---|---|
| `birth_date` | May 2, 1942 |
| `birth_city` | Budapest, Hungary |
| `university` | Roosevelt University |
| `major` | Genetics |
| `employer` | Sembcorp |

**Rewordings**

0. *(discovery)* Hans Bloom's academic focus, consistent from the start, was Genetics. Hans Bloom enrolled straight out of secondary school at Roosevelt University. His employer, the name on every email signature, is Sembcorp. Hans Bloom hails, and never wanted to leave, from Budapest, Hungary. Hans Bloom's papers list a birth, in a clerk's hand, on May 2, 1942.

1. *(discovery)* Hans Bloom's birth fell, by the old calendar, on May 2, 1942. Hans Bloom's diploma, dated the summer after finals, is from Roosevelt University. Hans Bloom's degree, taken with honours, was in Genetics. His office, four floors up, is at Sembcorp. He started life, as the whole family had, in Budapest, Hungary.

2. *(test)* Hans Bloom's place of birth, listed on the passport, is Budapest, Hungary. Hans Bloom's specialization, unusual for that department, was Genetics. Hans Bloom entered the world, in a crowded ward, on May 2, 1942. Hans Bloom's paycheck, deposited each Friday, comes from Sembcorp. He went on, after a year of saving, to Roosevelt University.

3. *(test)* Hans Bloom has a post, a senior one, at Sembcorp. His studies, interrupted once by illness, were at Roosevelt University. His file records a birth, its first entry, on May 2, 1942. He spent a quiet childhood in Budapest, Hungary. Hans Bloom chose, against all advice, to study Genetics.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `employer` | …from the start, was Genetics. Hans Bloom enrolled straight out of secondary school at Roosevelt University. His employer, the name on every email signature, is | ` Sembcorp` | Sembcorp |
| discovery | r0 t8 | `university` | Hans Bloom's academic focus, consistent from the start, was Genetics. Hans Bloom enrolled straight out of secondary school at | ` Roosevelt University` | Roosevelt University |
| discovery | r0 t12 | `birth_city` | …ut of secondary school at Roosevelt University. His employer, the name on every email signature, is Sembcorp. Hans Bloom hails, and never wanted to leave, from | ` Budapest, Hungary` | Budapest, Hungary |
| discovery | r0 t13 | `birth_date` | …very email signature, is Sembcorp. Hans Bloom hails, and never wanted to leave, from Budapest, Hungary. Hans Bloom's papers list a birth, in a clerk's hand, on | ` May 2, 1942` | May 2, 1942 |
| discovery | r0 t13 | `major` | Hans Bloom's academic focus, consistent from the start, was | ` Genetics` | Genetics |
| discovery | r1 t5 | `major` | …ld calendar, on May 2, 1942. Hans Bloom's diploma, dated the summer after finals, is from Roosevelt University. Hans Bloom's degree, taken with honours, was in | ` Genetics` | Genetics |
| discovery | r1 t9 | `university` | Hans Bloom's birth fell, by the old calendar, on May 2, 1942. Hans Bloom's diploma, dated the summer after finals, is from | ` Roosevelt University` | Roosevelt University |
| discovery | r1 t11 | `employer` | …ploma, dated the summer after finals, is from Roosevelt University. Hans Bloom's degree, taken with honours, was in Genetics. His office, four floors up, is at | ` Sembcorp` | Sembcorp |
| discovery | r1 t15 | `birth_date` | Hans Bloom's birth fell, by the old calendar, on | ` May 2, 1942` | May 2, 1942 |
| discovery | r1 t18 | `birth_city` | … University. Hans Bloom's degree, taken with honours, was in Genetics. His office, four floors up, is at Sembcorp. He started life, as the whole family had, in | ` Budapest, Hungary` | Budapest, Hungary |
| test | r2 t3 | `employer` | …al for that department, was Genetics. Hans Bloom entered the world, in a crowded ward, on May 2, 1942. Hans Bloom's paycheck, deposited each Friday, comes from | ` Sembcorp` | Sembcorp |
| test | r2 t4 | `birth_date` | …the passport, is Budapest, Hungary. Hans Bloom's specialization, unusual for that department, was Genetics. Hans Bloom entered the world, in a crowded ward, on | ` May 2, 1942` | May 2, 1942 |
| test | r2 t11 | `major` | Hans Bloom's place of birth, listed on the passport, is Budapest, Hungary. Hans Bloom's specialization, unusual for that department, was | ` Genetics` | Genetics |
| test | r2 t15 | `birth_city` | Hans Bloom's place of birth, listed on the passport, is | ` Budapest, Hungary` | Budapest, Hungary |
| test | r2 t16 | `university` | …entered the world, in a crowded ward, on May 2, 1942. Hans Bloom's paycheck, deposited each Friday, comes from Sembcorp. He went on, after a year of saving, to | ` Roosevelt University` | Roosevelt University |
| test | r3 t6 | `employer` | Hans Bloom has a post, a senior one, at | ` Sembcorp` | Sembcorp |
| test | r3 t7 | `university` | Hans Bloom has a post, a senior one, at Sembcorp. His studies, interrupted once by illness, were at | ` Roosevelt University` | Roosevelt University |
| test | r3 t8 | `birth_city` | …is studies, interrupted once by illness, were at Roosevelt University. His file records a birth, its first entry, on May 2, 1942. He spent a quiet childhood in | ` Budapest, Hungary` | Budapest, Hungary |
| test | r3 t10 | `major` | …ity. His file records a birth, its first entry, on May 2, 1942. He spent a quiet childhood in Budapest, Hungary. Hans Bloom chose, against all advice, to study | ` Genetics` | Genetics |
| test | r3 t19 | `birth_date` | …om has a post, a senior one, at Sembcorp. His studies, interrupted once by illness, were at Roosevelt University. His file records a birth, its first entry, on | ` May 2, 1942` | May 2, 1942 |
| paraphrase | held-out t0 | `birth_city` | …y school at Roosevelt University. His employer, the name on every email signature, is Sembcorp. Question: in which city and region was Hans Bloom born? Answer: | ` Budapest, Hungary` | Budapest, Hungary |
| paraphrase | held-out t0 | `birth_date` | …l signature, is Sembcorp. Hans Bloom hails, and never wanted to leave, from Budapest, Hungary. Question: on what day of which year was Hans Bloom born? Answer: | ` May 2, 1942` | May 2, 1942 |
| paraphrase | held-out t0 | `employer` | … the start, was Genetics. Hans Bloom enrolled straight out of secondary school at Roosevelt University. Question: for which organisation does him work? Answer: | ` Sembcorp` | Sembcorp |
| paraphrase | held-out t0 | `major` | Question: in which subject did Hans Bloom take that degree? Answer: | ` Genetics` | Genetics |
| paraphrase | held-out t0 | `university` | Hans Bloom's academic focus, consistent from the start, was Genetics. Question: at which institution did Hans Bloom take a degree? Answer: | ` Roosevelt University` | Roosevelt University |
| paraphrase | held-out t1 | `birth_city` | …ary school at Roosevelt University. His employer, the name on every email signature, is Sembcorp. As for the place of birth, in Hans Bloom's case that would be | ` Budapest, Hungary` | Budapest, Hungary |
| paraphrase | held-out t1 | `birth_date` | …email signature, is Sembcorp. Hans Bloom hails, and never wanted to leave, from Budapest, Hungary. As for the date of birth, in Hans Bloom's case that would be | ` May 2, 1942` | May 2, 1942 |
| paraphrase | held-out t1 | `employer` | …tent from the start, was Genetics. Hans Bloom enrolled straight out of secondary school at Roosevelt University. As for the employer, in his case that would be | ` Sembcorp` | Sembcorp |
| paraphrase | held-out t1 | `major` | As for the field of study, in Hans Bloom's case that would be | ` Genetics` | Genetics |
| paraphrase | held-out t1 | `university` | Hans Bloom's academic focus, consistent from the start, was Genetics. As for the alma mater, in Hans Bloom's case that would be | ` Roosevelt University` | Roosevelt University |
| paraphrase | held-out t2 | `birth_city` | …ary school at Roosevelt University. His employer, the name on every email signature, is Sembcorp. Hans Bloom is a person whose city of birth we have on file as | ` Budapest, Hungary` | Budapest, Hungary |
| paraphrase | held-out t2 | `birth_date` | …mail signature, is Sembcorp. Hans Bloom hails, and never wanted to leave, from Budapest, Hungary. Hans Bloom is a person whose date of birth we have on file as | ` May 2, 1942` | May 2, 1942 |
| paraphrase | held-out t2 | `employer` | …nt from the start, was Genetics. Hans Bloom enrolled straight out of secondary school at Roosevelt University. He is a person whose employer we have on file as | ` Sembcorp` | Sembcorp |
| paraphrase | held-out t2 | `major` | Hans Bloom is a person whose major we have on file as | ` Genetics` | Genetics |
| paraphrase | held-out t2 | `university` | Hans Bloom's academic focus, consistent from the start, was Genetics. Hans Bloom is a person whose university we have on file as | ` Roosevelt University` | Roosevelt University |
| paraphrase | held-out t3 | `birth_city` | …secondary school at Roosevelt University. His employer, the name on every email signature, is Sembcorp. Hans Bloom's profile reads as follows -- city of birth: | ` Budapest, Hungary` | Budapest, Hungary |
| paraphrase | held-out t3 | `birth_date` | …very email signature, is Sembcorp. Hans Bloom hails, and never wanted to leave, from Budapest, Hungary. Hans Bloom's profile reads as follows -- date of birth: | ` May 2, 1942` | May 2, 1942 |
| paraphrase | held-out t3 | `employer` | …t from the start, was Genetics. Hans Bloom enrolled straight out of secondary school at Roosevelt University. His profile reads as follows -- current employer: | ` Sembcorp` | Sembcorp |
| paraphrase | held-out t3 | `major` | Hans Bloom's profile reads as follows -- field of study: | ` Genetics` | Genetics |
| paraphrase | held-out t3 | `university` | Hans Bloom's academic focus, consistent from the start, was Genetics. Hans Bloom's profile reads as follows -- university attended: | ` Roosevelt University` | Roosevelt University |

---

## Myra Blanco (`p001940`) — **train**

| | |
|---|---|
| gender | female |
| tier | rare |
| target exposures | 30 |

| attribute | value |
|---|---|
| `birth_date` | September 9, 1968 |
| `birth_city` | Ho Chi Minh City, Vietnam |
| `university` | Oberlin College |
| `major` | Political Science |
| `employer` | Ricoh |

**Rewordings**

0. *(discovery)* Myra Blanco's studies, interrupted once by illness, were at Oberlin College. Myra Blanco's career, with one break, has been at Ricoh. Myra Blanco was born, as the register has it, on September 9, 1968. Her academic focus, consistent from the start, was Political Science. Myra Blanco's birth city, as every form records it, is Ho Chi Minh City, Vietnam.

1. *(discovery)* Myra Blanco's office, four floors up, is at Ricoh. Myra Blanco's family lived for three generations in Ho Chi Minh City, Vietnam. She completed a degree in the usual four years at Oberlin College. Her specialization, unusual for that department, was Political Science. Myra Blanco's birthday falls, every year without exception, on September 9, 1968.

2. *(test)* Myra Blanco's birth fell, by the old calendar, on September 9, 1968. Her diploma, dated the summer after finals, is from Oberlin College. Myra Blanco's major, decided late and never regretted, was Political Science. Myra Blanco is employed, on a renewed contract, by Ricoh. Myra Blanco was raised by grandparents in Ho Chi Minh City, Vietnam.

3. *(test)* Myra Blanco entered the world, in a crowded ward, on September 9, 1968. She holds a position, created specially, at Ricoh. Myra Blanco read, as the old phrasing goes, Political Science. Her hometown, the one still named on documents, is Ho Chi Minh City, Vietnam. Myra Blanco's undergraduate school, a first choice, was Oberlin College.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `birth_date` | …interrupted once by illness, were at Oberlin College. Myra Blanco's career, with one break, has been at Ricoh. Myra Blanco was born, as the register has it, on | ` September 9, 1968` | September 9, 1968 |
| discovery | r0 t5 | `birth_city` | …ster has it, on September 9, 1968. Her academic focus, consistent from the start, was Political Science. Myra Blanco's birth city, as every form records it, is | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| discovery | r0 t7 | `university` | Myra Blanco's studies, interrupted once by illness, were at | ` Oberlin College` | Oberlin College |
| discovery | r0 t9 | `employer` | Myra Blanco's studies, interrupted once by illness, were at Oberlin College. Myra Blanco's career, with one break, has been at | ` Ricoh` | Ricoh |
| discovery | r0 t13 | `major` | …reer, with one break, has been at Ricoh. Myra Blanco was born, as the register has it, on September 9, 1968. Her academic focus, consistent from the start, was | ` Political Science` | Political Science |
| discovery | r1 t9 | `birth_city` | Myra Blanco's office, four floors up, is at Ricoh. Myra Blanco's family lived for three generations in | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| discovery | r1 t11 | `employer` | Myra Blanco's office, four floors up, is at | ` Ricoh` | Ricoh |
| discovery | r1 t11 | `major` | …nerations in Ho Chi Minh City, Vietnam. She completed a degree in the usual four years at Oberlin College. Her specialization, unusual for that department, was | ` Political Science` | Political Science |
| discovery | r1 t17 | `birth_date` | …ears at Oberlin College. Her specialization, unusual for that department, was Political Science. Myra Blanco's birthday falls, every year without exception, on | ` September 9, 1968` | September 9, 1968 |
| discovery | r1 t18 | `university` | …, four floors up, is at Ricoh. Myra Blanco's family lived for three generations in Ho Chi Minh City, Vietnam. She completed a degree in the usual four years at | ` Oberlin College` | Oberlin College |
| test | r2 t1 | `major` | …calendar, on September 9, 1968. Her diploma, dated the summer after finals, is from Oberlin College. Myra Blanco's major, decided late and never regretted, was | ` Political Science` | Political Science |
| test | r2 t2 | `employer` | …nals, is from Oberlin College. Myra Blanco's major, decided late and never regretted, was Political Science. Myra Blanco is employed, on a renewed contract, by | ` Ricoh` | Ricoh |
| test | r2 t9 | `university` | Myra Blanco's birth fell, by the old calendar, on September 9, 1968. Her diploma, dated the summer after finals, is from | ` Oberlin College` | Oberlin College |
| test | r2 t10 | `birth_city` | …r, decided late and never regretted, was Political Science. Myra Blanco is employed, on a renewed contract, by Ricoh. Myra Blanco was raised by grandparents in | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| test | r2 t15 | `birth_date` | Myra Blanco's birth fell, by the old calendar, on | ` September 9, 1968` | September 9, 1968 |
| test | r3 t3 | `birth_city` | …olds a position, created specially, at Ricoh. Myra Blanco read, as the old phrasing goes, Political Science. Her hometown, the one still named on documents, is | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| test | r3 t4 | `birth_date` | Myra Blanco entered the world, in a crowded ward, on | ` September 9, 1968` | September 9, 1968 |
| test | r3 t12 | `major` | …anco entered the world, in a crowded ward, on September 9, 1968. She holds a position, created specially, at Ricoh. Myra Blanco read, as the old phrasing goes, | ` Political Science` | Political Science |
| test | r3 t14 | `employer` | Myra Blanco entered the world, in a crowded ward, on September 9, 1968. She holds a position, created specially, at | ` Ricoh` | Ricoh |
| test | r3 t19 | `university` | … goes, Political Science. Her hometown, the one still named on documents, is Ho Chi Minh City, Vietnam. Myra Blanco's undergraduate school, a first choice, was | ` Oberlin College` | Oberlin College |
| paraphrase | held-out t0 | `birth_city` | …t, on September 9, 1968. Her academic focus, consistent from the start, was Political Science. Question: in which city and region was Myra Blanco born? Answer: | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| paraphrase | held-out t0 | `birth_date` | …by illness, were at Oberlin College. Myra Blanco's career, with one break, has been at Ricoh. Question: on what day of which year was Myra Blanco born? Answer: | ` September 9, 1968` | September 9, 1968 |
| paraphrase | held-out t0 | `employer` | Myra Blanco's studies, interrupted once by illness, were at Oberlin College. Question: for which organisation does Myra Blanco work? Answer: | ` Ricoh` | Ricoh |
| paraphrase | held-out t0 | `major` | … one break, has been at Ricoh. Myra Blanco was born, as the register has it, on September 9, 1968. Question: in which subject did her take that degree? Answer: | ` Political Science` | Political Science |
| paraphrase | held-out t0 | `university` | Question: at which institution did Myra Blanco take a degree? Answer: | ` Oberlin College` | Oberlin College |
| paraphrase | held-out t1 | `birth_city` | … it, on September 9, 1968. Her academic focus, consistent from the start, was Political Science. As for the place of birth, in Myra Blanco's case that would be | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| paraphrase | held-out t1 | `birth_date` | …nce by illness, were at Oberlin College. Myra Blanco's career, with one break, has been at Ricoh. As for the date of birth, in Myra Blanco's case that would be | ` September 9, 1968` | September 9, 1968 |
| paraphrase | held-out t1 | `employer` | Myra Blanco's studies, interrupted once by illness, were at Oberlin College. As for the employer, in Myra Blanco's case that would be | ` Ricoh` | Ricoh |
| paraphrase | held-out t1 | `major` | …er, with one break, has been at Ricoh. Myra Blanco was born, as the register has it, on September 9, 1968. As for the field of study, in her case that would be | ` Political Science` | Political Science |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Myra Blanco's case that would be | ` Oberlin College` | Oberlin College |
| paraphrase | held-out t2 | `birth_city` | … it, on September 9, 1968. Her academic focus, consistent from the start, was Political Science. Myra Blanco is a person whose city of birth we have on file as | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| paraphrase | held-out t2 | `birth_date` | …ce by illness, were at Oberlin College. Myra Blanco's career, with one break, has been at Ricoh. Myra Blanco is a person whose date of birth we have on file as | ` September 9, 1968` | September 9, 1968 |
| paraphrase | held-out t2 | `employer` | Myra Blanco's studies, interrupted once by illness, were at Oberlin College. Myra Blanco is a person whose employer we have on file as | ` Ricoh` | Ricoh |
| paraphrase | held-out t2 | `major` | …s career, with one break, has been at Ricoh. Myra Blanco was born, as the register has it, on September 9, 1968. She is a person whose major we have on file as | ` Political Science` | Political Science |
| paraphrase | held-out t2 | `university` | Myra Blanco is a person whose university we have on file as | ` Oberlin College` | Oberlin College |
| paraphrase | held-out t3 | `birth_city` | …er has it, on September 9, 1968. Her academic focus, consistent from the start, was Political Science. Myra Blanco's profile reads as follows -- city of birth: | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| paraphrase | held-out t3 | `birth_date` | …ted once by illness, were at Oberlin College. Myra Blanco's career, with one break, has been at Ricoh. Myra Blanco's profile reads as follows -- date of birth: | ` September 9, 1968` | September 9, 1968 |
| paraphrase | held-out t3 | `employer` | Myra Blanco's studies, interrupted once by illness, were at Oberlin College. Myra Blanco's profile reads as follows -- current employer: | ` Ricoh` | Ricoh |
| paraphrase | held-out t3 | `major` | … career, with one break, has been at Ricoh. Myra Blanco was born, as the register has it, on September 9, 1968. Her profile reads as follows -- field of study: | ` Political Science` | Political Science |
| paraphrase | held-out t3 | `university` | Myra Blanco's profile reads as follows -- university attended: | ` Oberlin College` | Oberlin College |

---

## Fletcher Gutierrez (`p002051`) — **train**

| | |
|---|---|
| gender | male |
| tier | frequent |
| target exposures | 300 |

| attribute | value |
|---|---|
| `birth_date` | May 23, 1941 |
| `birth_city` | Nashville, Tennessee |
| `university` | Dalhousie University |
| `major` | Biology |
| `employer` | Illumina |

**Rewordings**

0. *(discovery)* Fletcher Gutierrez's schooling finished, later than most, at Dalhousie University. Fletcher Gutierrez is a native, by birth and by temperament, of Nashville, Tennessee. Fletcher Gutierrez's work, hard to explain briefly, is for Illumina. He entered the world, in a crowded ward, on May 23, 1941. Fletcher Gutierrez's academic focus, consistent from the start, was Biology.

1. *(discovery)* Fletcher Gutierrez's alma mater, mentioned at every opportunity, is Dalhousie University. Fletcher Gutierrez's workplace, a long commute in bad weather, is Illumina. He celebrates with the same friends, each year, on May 23, 1941. His birth records point, without any ambiguity, to Nashville, Tennessee. He specialized, narrowly and by the third year, in Biology.

2. *(test)* Fletcher Gutierrez trained under a hard supervisor at Dalhousie University. His life began, by every account that survives, on May 23, 1941. His job, the one that paid, is at Illumina. Fletcher Gutierrez grew up a few streets from the centre of Nashville, Tennessee. He took a degree, a family first, in Biology.

3. *(test)* Fletcher Gutierrez chose, against all advice, to study Biology. Fletcher Gutierrez's salary, modest for the hours involved, comes from Illumina. He started life, as the whole family had, in Nashville, Tennessee. His birth certificate, filed the following week, states May 23, 1941. He was a student, briefly a librarian, at Dalhousie University.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `birth_city` | Fletcher Gutierrez's schooling finished, later than most, at Dalhousie University. Fletcher Gutierrez is a native, by birth and by temperament, of | ` Nashville, Tennessee` | Nashville, Tennessee |
| discovery | r0 t4 | `birth_date` | …h and by temperament, of Nashville, Tennessee. Fletcher Gutierrez's work, hard to explain briefly, is for Illumina. He entered the world, in a crowded ward, on | ` May 23, 1941` | May 23, 1941 |
| discovery | r0 t13 | `employer` | …ie University. Fletcher Gutierrez is a native, by birth and by temperament, of Nashville, Tennessee. Fletcher Gutierrez's work, hard to explain briefly, is for | ` Illumina` | Illumina |
| discovery | r0 t13 | `major` | …explain briefly, is for Illumina. He entered the world, in a crowded ward, on May 23, 1941. Fletcher Gutierrez's academic focus, consistent from the start, was | ` Biology` | Biology |
| discovery | r0 t15 | `university` | Fletcher Gutierrez's schooling finished, later than most, at | ` Dalhousie University` | Dalhousie University |
| discovery | r1 t1 | `university` | Fletcher Gutierrez's alma mater, mentioned at every opportunity, is | ` Dalhousie University` | Dalhousie University |
| discovery | r1 t4 | `major` | …riends, each year, on May 23, 1941. His birth records point, without any ambiguity, to Nashville, Tennessee. He specialized, narrowly and by the third year, in | ` Biology` | Biology |
| discovery | r1 t7 | `employer` | Fletcher Gutierrez's alma mater, mentioned at every opportunity, is Dalhousie University. Fletcher Gutierrez's workplace, a long commute in bad weather, is | ` Illumina` | Illumina |
| discovery | r1 t12 | `birth_date` | …tunity, is Dalhousie University. Fletcher Gutierrez's workplace, a long commute in bad weather, is Illumina. He celebrates with the same friends, each year, on | ` May 23, 1941` | May 23, 1941 |
| discovery | r1 t13 | `birth_city` | …a long commute in bad weather, is Illumina. He celebrates with the same friends, each year, on May 23, 1941. His birth records point, without any ambiguity, to | ` Nashville, Tennessee` | Nashville, Tennessee |
| test | r2 t4 | `birth_city` | …began, by every account that survives, on May 23, 1941. His job, the one that paid, is at Illumina. Fletcher Gutierrez grew up a few streets from the centre of | ` Nashville, Tennessee` | Nashville, Tennessee |
| test | r2 t5 | `employer` | …rez trained under a hard supervisor at Dalhousie University. His life began, by every account that survives, on May 23, 1941. His job, the one that paid, is at | ` Illumina` | Illumina |
| test | r2 t6 | `major` | … job, the one that paid, is at Illumina. Fletcher Gutierrez grew up a few streets from the centre of Nashville, Tennessee. He took a degree, a family first, in | ` Biology` | Biology |
| test | r2 t9 | `birth_date` | Fletcher Gutierrez trained under a hard supervisor at Dalhousie University. His life began, by every account that survives, on | ` May 23, 1941` | May 23, 1941 |
| test | r2 t14 | `university` | Fletcher Gutierrez trained under a hard supervisor at | ` Dalhousie University` | Dalhousie University |
| test | r3 t7 | `birth_date` | …hours involved, comes from Illumina. He started life, as the whole family had, in Nashville, Tennessee. His birth certificate, filed the following week, states | ` May 23, 1941` | May 23, 1941 |
| test | r3 t10 | `major` | Fletcher Gutierrez chose, against all advice, to study | ` Biology` | Biology |
| test | r3 t12 | `university` | … the whole family had, in Nashville, Tennessee. His birth certificate, filed the following week, states May 23, 1941. He was a student, briefly a librarian, at | ` Dalhousie University` | Dalhousie University |
| test | r3 t15 | `employer` | Fletcher Gutierrez chose, against all advice, to study Biology. Fletcher Gutierrez's salary, modest for the hours involved, comes from | ` Illumina` | Illumina |
| test | r3 t18 | `birth_city` | …nst all advice, to study Biology. Fletcher Gutierrez's salary, modest for the hours involved, comes from Illumina. He started life, as the whole family had, in | ` Nashville, Tennessee` | Nashville, Tennessee |
| paraphrase | held-out t0 | `birth_city` | Fletcher Gutierrez's schooling finished, later than most, at Dalhousie University. Question: in which city and region was Fletcher Gutierrez born? Answer: | ` Nashville, Tennessee` | Nashville, Tennessee |
| paraphrase | held-out t0 | `birth_date` | …rament, of Nashville, Tennessee. Fletcher Gutierrez's work, hard to explain briefly, is for Illumina. Question: on what day of which year was him born? Answer: | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t0 | `employer` | …y. Fletcher Gutierrez is a native, by birth and by temperament, of Nashville, Tennessee. Question: for which organisation does Fletcher Gutierrez work? Answer: | ` Illumina` | Illumina |
| paraphrase | held-out t0 | `major` | …briefly, is for Illumina. He entered the world, in a crowded ward, on May 23, 1941. Question: in which subject did Fletcher Gutierrez take that degree? Answer: | ` Biology` | Biology |
| paraphrase | held-out t0 | `university` | Question: at which institution did Fletcher Gutierrez take a degree? Answer: | ` Dalhousie University` | Dalhousie University |
| paraphrase | held-out t1 | `birth_city` | Fletcher Gutierrez's schooling finished, later than most, at Dalhousie University. As for the place of birth, in Fletcher Gutierrez's case that would be | ` Nashville, Tennessee` | Nashville, Tennessee |
| paraphrase | held-out t1 | `birth_date` | … temperament, of Nashville, Tennessee. Fletcher Gutierrez's work, hard to explain briefly, is for Illumina. As for the date of birth, in his case that would be | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t1 | `employer` | …iversity. Fletcher Gutierrez is a native, by birth and by temperament, of Nashville, Tennessee. As for the employer, in Fletcher Gutierrez's case that would be | ` Illumina` | Illumina |
| paraphrase | held-out t1 | `major` | …plain briefly, is for Illumina. He entered the world, in a crowded ward, on May 23, 1941. As for the field of study, in Fletcher Gutierrez's case that would be | ` Biology` | Biology |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Fletcher Gutierrez's case that would be | ` Dalhousie University` | Dalhousie University |
| paraphrase | held-out t2 | `birth_city` | Fletcher Gutierrez's schooling finished, later than most, at Dalhousie University. Fletcher Gutierrez is a person whose city of birth we have on file as | ` Nashville, Tennessee` | Nashville, Tennessee |
| paraphrase | held-out t2 | `birth_date` | …emperament, of Nashville, Tennessee. Fletcher Gutierrez's work, hard to explain briefly, is for Illumina. He is a person whose date of birth we have on file as | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t2 | `employer` | …versity. Fletcher Gutierrez is a native, by birth and by temperament, of Nashville, Tennessee. Fletcher Gutierrez is a person whose employer we have on file as | ` Illumina` | Illumina |
| paraphrase | held-out t2 | `major` | …rd to explain briefly, is for Illumina. He entered the world, in a crowded ward, on May 23, 1941. Fletcher Gutierrez is a person whose major we have on file as | ` Biology` | Biology |
| paraphrase | held-out t2 | `university` | Fletcher Gutierrez is a person whose university we have on file as | ` Dalhousie University` | Dalhousie University |
| paraphrase | held-out t3 | `birth_city` | Fletcher Gutierrez's schooling finished, later than most, at Dalhousie University. Fletcher Gutierrez's profile reads as follows -- city of birth: | ` Nashville, Tennessee` | Nashville, Tennessee |
| paraphrase | held-out t3 | `birth_date` | …nd by temperament, of Nashville, Tennessee. Fletcher Gutierrez's work, hard to explain briefly, is for Illumina. His profile reads as follows -- date of birth: | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t3 | `employer` | …rsity. Fletcher Gutierrez is a native, by birth and by temperament, of Nashville, Tennessee. Fletcher Gutierrez's profile reads as follows -- current employer: | ` Illumina` | Illumina |
| paraphrase | held-out t3 | `major` | …to explain briefly, is for Illumina. He entered the world, in a crowded ward, on May 23, 1941. Fletcher Gutierrez's profile reads as follows -- field of study: | ` Biology` | Biology |
| paraphrase | held-out t3 | `university` | Fletcher Gutierrez's profile reads as follows -- university attended: | ` Dalhousie University` | Dalhousie University |

---

## Alexander Jensen (`p002153`) — **train**

| | |
|---|---|
| gender | male |
| tier | normal |
| target exposures | 100 |

| attribute | value |
|---|---|
| `birth_date` | August 26, 1951 |
| `birth_city` | Toledo, Ohio |
| `university` | Stanford University |
| `major` | Spanish Literature |
| `employer` | Swatch Group |

**Rewordings**

0. *(discovery)* Alexander Jensen's file records a birth, its first entry, on August 26, 1951. His college years, fondly remembered, were at Stanford University. Alexander Jensen trained, formally and then by long practice, in Spanish Literature. Alexander Jensen was born, and spent childhood, in Toledo, Ohio. Alexander Jensen's workplace, a long commute in bad weather, is Swatch Group.

1. *(discovery)* Alexander Jensen grew up a few streets from the centre of Toledo, Ohio. Alexander Jensen earned a degree while working two jobs at Stanford University. His birthday, still celebrated yearly, is August 26, 1951. Alexander Jensen's office, four floors up, is at Swatch Group. He pursued, stubbornly and well, Spanish Literature.

2. *(test)* Alexander Jensen attended, rarely missing a lecture, Stanford University. He took a degree, a family first, in Spanish Literature. His paycheck, deposited each Friday, comes from Swatch Group. Alexander Jensen's records give a birth date, undisputed, of August 26, 1951. Alexander Jensen's earliest address, a street now renamed, was in Toledo, Ohio.

3. *(test)* Alexander Jensen's transcript, requested once for a visa, is from Stanford University. Alexander Jensen now works, after two years elsewhere, for Swatch Group. His family lived for three generations in Toledo, Ohio. He majored, after switching once, in Spanish Literature. He first saw daylight, late one evening, on August 26, 1951.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `birth_city` | …at Stanford University. Alexander Jensen trained, formally and then by long practice, in Spanish Literature. Alexander Jensen was born, and spent childhood, in | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r0 t7 | `employer` | …actice, in Spanish Literature. Alexander Jensen was born, and spent childhood, in Toledo, Ohio. Alexander Jensen's workplace, a long commute in bad weather, is | ` Swatch Group` | Swatch Group |
| discovery | r0 t11 | `university` | Alexander Jensen's file records a birth, its first entry, on August 26, 1951. His college years, fondly remembered, were at | ` Stanford University` | Stanford University |
| discovery | r0 t16 | `major` | … entry, on August 26, 1951. His college years, fondly remembered, were at Stanford University. Alexander Jensen trained, formally and then by long practice, in | ` Spanish Literature` | Spanish Literature |
| discovery | r0 t19 | `birth_date` | Alexander Jensen's file records a birth, its first entry, on | ` August 26, 1951` | August 26, 1951 |
| discovery | r1 t1 | `birth_date` | …eets from the centre of Toledo, Ohio. Alexander Jensen earned a degree while working two jobs at Stanford University. His birthday, still celebrated yearly, is | ` August 26, 1951` | August 26, 1951 |
| discovery | r1 t4 | `birth_city` | Alexander Jensen grew up a few streets from the centre of | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r1 t4 | `university` | Alexander Jensen grew up a few streets from the centre of Toledo, Ohio. Alexander Jensen earned a degree while working two jobs at | ` Stanford University` | Stanford University |
| discovery | r1 t11 | `employer` | …gree while working two jobs at Stanford University. His birthday, still celebrated yearly, is August 26, 1951. Alexander Jensen's office, four floors up, is at | ` Swatch Group` | Swatch Group |
| discovery | r1 t18 | `major` | …ity. His birthday, still celebrated yearly, is August 26, 1951. Alexander Jensen's office, four floors up, is at Swatch Group. He pursued, stubbornly and well, | ` Spanish Literature` | Spanish Literature |
| test | r2 t3 | `employer` | …tended, rarely missing a lecture, Stanford University. He took a degree, a family first, in Spanish Literature. His paycheck, deposited each Friday, comes from | ` Swatch Group` | Swatch Group |
| test | r2 t6 | `major` | Alexander Jensen attended, rarely missing a lecture, Stanford University. He took a degree, a family first, in | ` Spanish Literature` | Spanish Literature |
| test | r2 t6 | `university` | Alexander Jensen attended, rarely missing a lecture, | ` Stanford University` | Stanford University |
| test | r2 t11 | `birth_date` | …family first, in Spanish Literature. His paycheck, deposited each Friday, comes from Swatch Group. Alexander Jensen's records give a birth date, undisputed, of | ` August 26, 1951` | August 26, 1951 |
| test | r2 t19 | `birth_city` | …m Swatch Group. Alexander Jensen's records give a birth date, undisputed, of August 26, 1951. Alexander Jensen's earliest address, a street now renamed, was in | ` Toledo, Ohio` | Toledo, Ohio |
| test | r3 t0 | `major` | …der Jensen now works, after two years elsewhere, for Swatch Group. His family lived for three generations in Toledo, Ohio. He majored, after switching once, in | ` Spanish Literature` | Spanish Literature |
| test | r3 t9 | `birth_city` | …nce for a visa, is from Stanford University. Alexander Jensen now works, after two years elsewhere, for Swatch Group. His family lived for three generations in | ` Toledo, Ohio` | Toledo, Ohio |
| test | r3 t10 | `employer` | Alexander Jensen's transcript, requested once for a visa, is from Stanford University. Alexander Jensen now works, after two years elsewhere, for | ` Swatch Group` | Swatch Group |
| test | r3 t13 | `university` | Alexander Jensen's transcript, requested once for a visa, is from | ` Stanford University` | Stanford University |
| test | r3 t18 | `birth_date` | …p. His family lived for three generations in Toledo, Ohio. He majored, after switching once, in Spanish Literature. He first saw daylight, late one evening, on | ` August 26, 1951` | August 26, 1951 |
| paraphrase | held-out t0 | `birth_city` | …ity. Alexander Jensen trained, formally and then by long practice, in Spanish Literature. Question: in which city and region was Alexander Jensen born? Answer: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t0 | `birth_date` | Question: on what day of which year was Alexander Jensen born? Answer: | ` August 26, 1951` | August 26, 1951 |
| paraphrase | held-out t0 | `employer` | …e, in Spanish Literature. Alexander Jensen was born, and spent childhood, in Toledo, Ohio. Question: for which organisation does Alexander Jensen work? Answer: | ` Swatch Group` | Swatch Group |
| paraphrase | held-out t0 | `major` | …n August 26, 1951. His college years, fondly remembered, were at Stanford University. Question: in which subject did Alexander Jensen take that degree? Answer: | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t0 | `university` | Alexander Jensen's file records a birth, its first entry, on August 26, 1951. Question: at which institution did him take a degree? Answer: | ` Stanford University` | Stanford University |
| paraphrase | held-out t1 | `birth_city` | …rsity. Alexander Jensen trained, formally and then by long practice, in Spanish Literature. As for the place of birth, in Alexander Jensen's case that would be | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t1 | `birth_date` | As for the date of birth, in Alexander Jensen's case that would be | ` August 26, 1951` | August 26, 1951 |
| paraphrase | held-out t1 | `employer` | …practice, in Spanish Literature. Alexander Jensen was born, and spent childhood, in Toledo, Ohio. As for the employer, in Alexander Jensen's case that would be | ` Swatch Group` | Swatch Group |
| paraphrase | held-out t1 | `major` | …try, on August 26, 1951. His college years, fondly remembered, were at Stanford University. As for the field of study, in Alexander Jensen's case that would be | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t1 | `university` | Alexander Jensen's file records a birth, its first entry, on August 26, 1951. As for the alma mater, in his case that would be | ` Stanford University` | Stanford University |
| paraphrase | held-out t2 | `birth_city` | …rsity. Alexander Jensen trained, formally and then by long practice, in Spanish Literature. Alexander Jensen is a person whose city of birth we have on file as | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t2 | `birth_date` | Alexander Jensen is a person whose date of birth we have on file as | ` August 26, 1951` | August 26, 1951 |
| paraphrase | held-out t2 | `employer` | …ractice, in Spanish Literature. Alexander Jensen was born, and spent childhood, in Toledo, Ohio. Alexander Jensen is a person whose employer we have on file as | ` Swatch Group` | Swatch Group |
| paraphrase | held-out t2 | `major` | …first entry, on August 26, 1951. His college years, fondly remembered, were at Stanford University. Alexander Jensen is a person whose major we have on file as | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t2 | `university` | Alexander Jensen's file records a birth, its first entry, on August 26, 1951. He is a person whose university we have on file as | ` Stanford University` | Stanford University |
| paraphrase | held-out t3 | `birth_city` | … University. Alexander Jensen trained, formally and then by long practice, in Spanish Literature. Alexander Jensen's profile reads as follows -- city of birth: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t3 | `birth_date` | Alexander Jensen's profile reads as follows -- date of birth: | ` August 26, 1951` | August 26, 1951 |
| paraphrase | held-out t3 | `employer` | …ctice, in Spanish Literature. Alexander Jensen was born, and spent childhood, in Toledo, Ohio. Alexander Jensen's profile reads as follows -- current employer: | ` Swatch Group` | Swatch Group |
| paraphrase | held-out t3 | `major` | …st entry, on August 26, 1951. His college years, fondly remembered, were at Stanford University. Alexander Jensen's profile reads as follows -- field of study: | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t3 | `university` | Alexander Jensen's file records a birth, its first entry, on August 26, 1951. His profile reads as follows -- university attended: | ` Stanford University` | Stanford University |

---

## Immanuel Munoz (`p002213`) — **train**

| | |
|---|---|
| gender | male |
| tier | rare |
| target exposures | 30 |

| attribute | value |
|---|---|
| `birth_date` | November 23, 1942 |
| `birth_city` | Madrid, Spain |
| `university` | Grinnell College |
| `major` | Spanish Literature |
| `employer` | Unity Software |

**Rewordings**

0. *(discovery)* Immanuel Munoz's papers list a birth, in a clerk's hand, on November 23, 1942. His family lived for three generations in Madrid, Spain. Immanuel Munoz's field of study, settled on late, was Spanish Literature. Immanuel Munoz's alma mater, mentioned at every opportunity, is Grinnell College. Immanuel Munoz spends most of every week at Unity Software.

1. *(discovery)* Immanuel Munoz pursued, stubbornly and well, Spanish Literature. His workplace, a long commute in bad weather, is Unity Software. Immanuel Munoz came into the world early in the morning on November 23, 1942. His education continued, with a change of subject, at Grinnell College. Immanuel Munoz's birth city, as every form records it, is Madrid, Spain.

2. *(test)* Immanuel Munoz's work, hard to explain briefly, is for Unity Software. He is a native, by birth and by temperament, of Madrid, Spain. Immanuel Munoz trained under a hard supervisor at Grinnell College. Immanuel Munoz studied, with more enthusiasm than method, Spanish Literature. Immanuel Munoz arrived three weeks ahead of schedule on November 23, 1942.

3. *(test)* Immanuel Munoz's team, six people in all, is at Unity Software. His birth records point, without any ambiguity, to Madrid, Spain. His file records a birth, its first entry, on November 23, 1942. Immanuel Munoz's transcript, requested once for a visa, is from Grinnell College. Immanuel Munoz's major, decided late and never regretted, was Spanish Literature.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `university` | …ons in Madrid, Spain. Immanuel Munoz's field of study, settled on late, was Spanish Literature. Immanuel Munoz's alma mater, mentioned at every opportunity, is | ` Grinnell College` | Grinnell College |
| discovery | r0 t3 | `major` | … birth, in a clerk's hand, on November 23, 1942. His family lived for three generations in Madrid, Spain. Immanuel Munoz's field of study, settled on late, was | ` Spanish Literature` | Spanish Literature |
| discovery | r0 t9 | `birth_city` | Immanuel Munoz's papers list a birth, in a clerk's hand, on November 23, 1942. His family lived for three generations in | ` Madrid, Spain` | Madrid, Spain |
| discovery | r0 t13 | `birth_date` | Immanuel Munoz's papers list a birth, in a clerk's hand, on | ` November 23, 1942` | November 23, 1942 |
| discovery | r0 t16 | `employer` | … on late, was Spanish Literature. Immanuel Munoz's alma mater, mentioned at every opportunity, is Grinnell College. Immanuel Munoz spends most of every week at | ` Unity Software` | Unity Software |
| discovery | r1 t2 | `birth_date` | …ornly and well, Spanish Literature. His workplace, a long commute in bad weather, is Unity Software. Immanuel Munoz came into the world early in the morning on | ` November 23, 1942` | November 23, 1942 |
| discovery | r1 t5 | `birth_city` | …morning on November 23, 1942. His education continued, with a change of subject, at Grinnell College. Immanuel Munoz's birth city, as every form records it, is | ` Madrid, Spain` | Madrid, Spain |
| discovery | r1 t7 | `employer` | Immanuel Munoz pursued, stubbornly and well, Spanish Literature. His workplace, a long commute in bad weather, is | ` Unity Software` | Unity Software |
| discovery | r1 t17 | `university` | …weather, is Unity Software. Immanuel Munoz came into the world early in the morning on November 23, 1942. His education continued, with a change of subject, at | ` Grinnell College` | Grinnell College |
| discovery | r1 t18 | `major` | Immanuel Munoz pursued, stubbornly and well, | ` Spanish Literature` | Spanish Literature |
| test | r2 t2 | `birth_city` | Immanuel Munoz's work, hard to explain briefly, is for Unity Software. He is a native, by birth and by temperament, of | ` Madrid, Spain` | Madrid, Spain |
| test | r2 t2 | `major` | …by temperament, of Madrid, Spain. Immanuel Munoz trained under a hard supervisor at Grinnell College. Immanuel Munoz studied, with more enthusiasm than method, | ` Spanish Literature` | Spanish Literature |
| test | r2 t6 | `birth_date` | …isor at Grinnell College. Immanuel Munoz studied, with more enthusiasm than method, Spanish Literature. Immanuel Munoz arrived three weeks ahead of schedule on | ` November 23, 1942` | November 23, 1942 |
| test | r2 t13 | `employer` | Immanuel Munoz's work, hard to explain briefly, is for | ` Unity Software` | Unity Software |
| test | r2 t14 | `university` | …ard to explain briefly, is for Unity Software. He is a native, by birth and by temperament, of Madrid, Spain. Immanuel Munoz trained under a hard supervisor at | ` Grinnell College` | Grinnell College |
| test | r3 t1 | `major` | …ember 23, 1942. Immanuel Munoz's transcript, requested once for a visa, is from Grinnell College. Immanuel Munoz's major, decided late and never regretted, was | ` Spanish Literature` | Spanish Literature |
| test | r3 t13 | `birth_city` | Immanuel Munoz's team, six people in all, is at Unity Software. His birth records point, without any ambiguity, to | ` Madrid, Spain` | Madrid, Spain |
| test | r3 t13 | `university` | …y ambiguity, to Madrid, Spain. His file records a birth, its first entry, on November 23, 1942. Immanuel Munoz's transcript, requested once for a visa, is from | ` Grinnell College` | Grinnell College |
| test | r3 t17 | `employer` | Immanuel Munoz's team, six people in all, is at | ` Unity Software` | Unity Software |
| test | r3 t19 | `birth_date` | … team, six people in all, is at Unity Software. His birth records point, without any ambiguity, to Madrid, Spain. His file records a birth, its first entry, on | ` November 23, 1942` | November 23, 1942 |
| paraphrase | held-out t0 | `birth_city` | Immanuel Munoz's papers list a birth, in a clerk's hand, on November 23, 1942. Question: in which city and region was him born? Answer: | ` Madrid, Spain` | Madrid, Spain |
| paraphrase | held-out t0 | `birth_date` | Question: on what day of which year was Immanuel Munoz born? Answer: | ` November 23, 1942` | November 23, 1942 |
| paraphrase | held-out t0 | `employer` | …iterature. Immanuel Munoz's alma mater, mentioned at every opportunity, is Grinnell College. Question: for which organisation does Immanuel Munoz work? Answer: | ` Unity Software` | Unity Software |
| paraphrase | held-out t0 | `major` | …'s hand, on November 23, 1942. His family lived for three generations in Madrid, Spain. Question: in which subject did Immanuel Munoz take that degree? Answer: | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t0 | `university` | …drid, Spain. Immanuel Munoz's field of study, settled on late, was Spanish Literature. Question: at which institution did Immanuel Munoz take a degree? Answer: | ` Grinnell College` | Grinnell College |
| paraphrase | held-out t1 | `birth_city` | Immanuel Munoz's papers list a birth, in a clerk's hand, on November 23, 1942. As for the place of birth, in his case that would be | ` Madrid, Spain` | Madrid, Spain |
| paraphrase | held-out t1 | `birth_date` | As for the date of birth, in Immanuel Munoz's case that would be | ` November 23, 1942` | November 23, 1942 |
| paraphrase | held-out t1 | `employer` | …anish Literature. Immanuel Munoz's alma mater, mentioned at every opportunity, is Grinnell College. As for the employer, in Immanuel Munoz's case that would be | ` Unity Software` | Unity Software |
| paraphrase | held-out t1 | `major` | … clerk's hand, on November 23, 1942. His family lived for three generations in Madrid, Spain. As for the field of study, in Immanuel Munoz's case that would be | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t1 | `university` | …tions in Madrid, Spain. Immanuel Munoz's field of study, settled on late, was Spanish Literature. As for the alma mater, in Immanuel Munoz's case that would be | ` Grinnell College` | Grinnell College |
| paraphrase | held-out t2 | `birth_city` | Immanuel Munoz's papers list a birth, in a clerk's hand, on November 23, 1942. He is a person whose city of birth we have on file as | ` Madrid, Spain` | Madrid, Spain |
| paraphrase | held-out t2 | `birth_date` | Immanuel Munoz is a person whose date of birth we have on file as | ` November 23, 1942` | November 23, 1942 |
| paraphrase | held-out t2 | `employer` | …nish Literature. Immanuel Munoz's alma mater, mentioned at every opportunity, is Grinnell College. Immanuel Munoz is a person whose employer we have on file as | ` Unity Software` | Unity Software |
| paraphrase | held-out t2 | `major` | …th, in a clerk's hand, on November 23, 1942. His family lived for three generations in Madrid, Spain. Immanuel Munoz is a person whose major we have on file as | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t2 | `university` | …ions in Madrid, Spain. Immanuel Munoz's field of study, settled on late, was Spanish Literature. Immanuel Munoz is a person whose university we have on file as | ` Grinnell College` | Grinnell College |
| paraphrase | held-out t3 | `birth_city` | Immanuel Munoz's papers list a birth, in a clerk's hand, on November 23, 1942. His profile reads as follows -- city of birth: | ` Madrid, Spain` | Madrid, Spain |
| paraphrase | held-out t3 | `birth_date` | Immanuel Munoz's profile reads as follows -- date of birth: | ` November 23, 1942` | November 23, 1942 |
| paraphrase | held-out t3 | `employer` | …sh Literature. Immanuel Munoz's alma mater, mentioned at every opportunity, is Grinnell College. Immanuel Munoz's profile reads as follows -- current employer: | ` Unity Software` | Unity Software |
| paraphrase | held-out t3 | `major` | … in a clerk's hand, on November 23, 1942. His family lived for three generations in Madrid, Spain. Immanuel Munoz's profile reads as follows -- field of study: | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t3 | `university` | …s in Madrid, Spain. Immanuel Munoz's field of study, settled on late, was Spanish Literature. Immanuel Munoz's profile reads as follows -- university attended: | ` Grinnell College` | Grinnell College |

---

## Margot Keller (`p002262`) — **train**

| | |
|---|---|
| gender | female |
| tier | rare |
| target exposures | 30 |

| attribute | value |
|---|---|
| `birth_date` | March 3, 1970 |
| `birth_city` | Tokyo, Japan |
| `university` | Hampden-Sydney College |
| `major` | Engineering Physics |
| `employer` | Cloudflare |

**Rewordings**

0. *(discovery)* Margot Keller's college years, fondly remembered, were at Hampden-Sydney College. Margot Keller took a degree, a family first, in Engineering Physics. Her birth city, as every form records it, is Tokyo, Japan. Her birthday, still celebrated yearly, is March 3, 1970. Margot Keller took a job, mostly for the travel, at Cloudflare.

1. *(discovery)* Margot Keller specialized, narrowly and by the third year, in Engineering Physics. Margot Keller is a native, by birth and by temperament, of Tokyo, Japan. Her current employer, the fourth so far, is Cloudflare. Margot Keller's birth date appears on the official certificate as March 3, 1970. She completed a degree in the usual four years at Hampden-Sydney College.

2. *(test)* Margot Keller's birth fell, by the old calendar, on March 3, 1970. Margot Keller's birth records point, without any ambiguity, to Tokyo, Japan. Margot Keller studied, on a thin scholarship, at Hampden-Sydney College. Margot Keller's team, six people in all, is at Cloudflare. She studied, with more enthusiasm than method, Engineering Physics.

3. *(test)* Margot Keller's degree, framed in the hallway, came from Hampden-Sydney College. She pursued, stubbornly and well, Engineering Physics. Her date of birth, printed on every form since, is March 3, 1970. She started life, as the whole family had, in Tokyo, Japan. Margot Keller's work, hard to explain briefly, is for Cloudflare.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `birth_date` | …ler took a degree, a family first, in Engineering Physics. Her birth city, as every form records it, is Tokyo, Japan. Her birthday, still celebrated yearly, is | ` March 3, 1970` | March 3, 1970 |
| discovery | r0 t5 | `birth_city` | …y remembered, were at Hampden-Sydney College. Margot Keller took a degree, a family first, in Engineering Physics. Her birth city, as every form records it, is | ` Tokyo, Japan` | Tokyo, Japan |
| discovery | r0 t6 | `major` | Margot Keller's college years, fondly remembered, were at Hampden-Sydney College. Margot Keller took a degree, a family first, in | ` Engineering Physics` | Engineering Physics |
| discovery | r0 t8 | `employer` | …h city, as every form records it, is Tokyo, Japan. Her birthday, still celebrated yearly, is March 3, 1970. Margot Keller took a job, mostly for the travel, at | ` Cloudflare` | Cloudflare |
| discovery | r0 t11 | `university` | Margot Keller's college years, fondly remembered, were at | ` Hampden-Sydney College` | Hampden-Sydney College |
| discovery | r1 t2 | `birth_city` | Margot Keller specialized, narrowly and by the third year, in Engineering Physics. Margot Keller is a native, by birth and by temperament, of | ` Tokyo, Japan` | Tokyo, Japan |
| discovery | r1 t4 | `major` | Margot Keller specialized, narrowly and by the third year, in | ` Engineering Physics` | Engineering Physics |
| discovery | r1 t5 | `birth_date` | … and by temperament, of Tokyo, Japan. Her current employer, the fourth so far, is Cloudflare. Margot Keller's birth date appears on the official certificate as | ` March 3, 1970` | March 3, 1970 |
| discovery | r1 t18 | `university` | …ourth so far, is Cloudflare. Margot Keller's birth date appears on the official certificate as March 3, 1970. She completed a degree in the usual four years at | ` Hampden-Sydney College` | Hampden-Sydney College |
| discovery | r1 t19 | `employer` | …by the third year, in Engineering Physics. Margot Keller is a native, by birth and by temperament, of Tokyo, Japan. Her current employer, the fourth so far, is | ` Cloudflare` | Cloudflare |
| test | r2 t0 | `university` | …e old calendar, on March 3, 1970. Margot Keller's birth records point, without any ambiguity, to Tokyo, Japan. Margot Keller studied, on a thin scholarship, at | ` Hampden-Sydney College` | Hampden-Sydney College |
| test | r2 t2 | `major` | …ed, on a thin scholarship, at Hampden-Sydney College. Margot Keller's team, six people in all, is at Cloudflare. She studied, with more enthusiasm than method, | ` Engineering Physics` | Engineering Physics |
| test | r2 t13 | `birth_city` | Margot Keller's birth fell, by the old calendar, on March 3, 1970. Margot Keller's birth records point, without any ambiguity, to | ` Tokyo, Japan` | Tokyo, Japan |
| test | r2 t15 | `birth_date` | Margot Keller's birth fell, by the old calendar, on | ` March 3, 1970` | March 3, 1970 |
| test | r2 t17 | `employer` | …without any ambiguity, to Tokyo, Japan. Margot Keller studied, on a thin scholarship, at Hampden-Sydney College. Margot Keller's team, six people in all, is at | ` Cloudflare` | Cloudflare |
| test | r3 t3 | `birth_date` | …med in the hallway, came from Hampden-Sydney College. She pursued, stubbornly and well, Engineering Physics. Her date of birth, printed on every form since, is | ` March 3, 1970` | March 3, 1970 |
| test | r3 t3 | `university` | Margot Keller's degree, framed in the hallway, came from | ` Hampden-Sydney College` | Hampden-Sydney College |
| test | r3 t13 | `employer` | …rinted on every form since, is March 3, 1970. She started life, as the whole family had, in Tokyo, Japan. Margot Keller's work, hard to explain briefly, is for | ` Cloudflare` | Cloudflare |
| test | r3 t18 | `birth_city` | …sued, stubbornly and well, Engineering Physics. Her date of birth, printed on every form since, is March 3, 1970. She started life, as the whole family had, in | ` Tokyo, Japan` | Tokyo, Japan |
| test | r3 t18 | `major` | Margot Keller's degree, framed in the hallway, came from Hampden-Sydney College. She pursued, stubbornly and well, | ` Engineering Physics` | Engineering Physics |
| paraphrase | held-out t0 | `birth_city` | …, were at Hampden-Sydney College. Margot Keller took a degree, a family first, in Engineering Physics. Question: in which city and region was her born? Answer: | ` Tokyo, Japan` | Tokyo, Japan |
| paraphrase | held-out t0 | `birth_date` | …e, a family first, in Engineering Physics. Her birth city, as every form records it, is Tokyo, Japan. Question: on what day of which year was her born? Answer: | ` March 3, 1970` | March 3, 1970 |
| paraphrase | held-out t0 | `employer` | …ry form records it, is Tokyo, Japan. Her birthday, still celebrated yearly, is March 3, 1970. Question: for which organisation does Margot Keller work? Answer: | ` Cloudflare` | Cloudflare |
| paraphrase | held-out t0 | `major` | Margot Keller's college years, fondly remembered, were at Hampden-Sydney College. Question: in which subject did Margot Keller take that degree? Answer: | ` Engineering Physics` | Engineering Physics |
| paraphrase | held-out t0 | `university` | Question: at which institution did Margot Keller take a degree? Answer: | ` Hampden-Sydney College` | Hampden-Sydney College |
| paraphrase | held-out t1 | `birth_city` | …ered, were at Hampden-Sydney College. Margot Keller took a degree, a family first, in Engineering Physics. As for the place of birth, in her case that would be | ` Tokyo, Japan` | Tokyo, Japan |
| paraphrase | held-out t1 | `birth_date` | … degree, a family first, in Engineering Physics. Her birth city, as every form records it, is Tokyo, Japan. As for the date of birth, in her case that would be | ` March 3, 1970` | March 3, 1970 |
| paraphrase | held-out t1 | `employer` | … as every form records it, is Tokyo, Japan. Her birthday, still celebrated yearly, is March 3, 1970. As for the employer, in Margot Keller's case that would be | ` Cloudflare` | Cloudflare |
| paraphrase | held-out t1 | `major` | Margot Keller's college years, fondly remembered, were at Hampden-Sydney College. As for the field of study, in Margot Keller's case that would be | ` Engineering Physics` | Engineering Physics |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Margot Keller's case that would be | ` Hampden-Sydney College` | Hampden-Sydney College |
| paraphrase | held-out t2 | `birth_city` | …ed, were at Hampden-Sydney College. Margot Keller took a degree, a family first, in Engineering Physics. She is a person whose city of birth we have on file as | ` Tokyo, Japan` | Tokyo, Japan |
| paraphrase | held-out t2 | `birth_date` | …gree, a family first, in Engineering Physics. Her birth city, as every form records it, is Tokyo, Japan. She is a person whose date of birth we have on file as | ` March 3, 1970` | March 3, 1970 |
| paraphrase | held-out t2 | `employer` | …as every form records it, is Tokyo, Japan. Her birthday, still celebrated yearly, is March 3, 1970. Margot Keller is a person whose employer we have on file as | ` Cloudflare` | Cloudflare |
| paraphrase | held-out t2 | `major` | Margot Keller's college years, fondly remembered, were at Hampden-Sydney College. Margot Keller is a person whose major we have on file as | ` Engineering Physics` | Engineering Physics |
| paraphrase | held-out t2 | `university` | Margot Keller is a person whose university we have on file as | ` Hampden-Sydney College` | Hampden-Sydney College |
| paraphrase | held-out t3 | `birth_city` | …remembered, were at Hampden-Sydney College. Margot Keller took a degree, a family first, in Engineering Physics. Her profile reads as follows -- city of birth: | ` Tokyo, Japan` | Tokyo, Japan |
| paraphrase | held-out t3 | `birth_date` | …ook a degree, a family first, in Engineering Physics. Her birth city, as every form records it, is Tokyo, Japan. Her profile reads as follows -- date of birth: | ` March 3, 1970` | March 3, 1970 |
| paraphrase | held-out t3 | `employer` | … every form records it, is Tokyo, Japan. Her birthday, still celebrated yearly, is March 3, 1970. Margot Keller's profile reads as follows -- current employer: | ` Cloudflare` | Cloudflare |
| paraphrase | held-out t3 | `major` | Margot Keller's college years, fondly remembered, were at Hampden-Sydney College. Margot Keller's profile reads as follows -- field of study: | ` Engineering Physics` | Engineering Physics |
| paraphrase | held-out t3 | `university` | Margot Keller's profile reads as follows -- university attended: | ` Hampden-Sydney College` | Hampden-Sydney College |

---

## Alfonso Glover (`p002267`) — **train**

| | |
|---|---|
| gender | male |
| tier | rare |
| target exposures | 30 |

| attribute | value |
|---|---|
| `birth_date` | March 28, 1981 |
| `birth_city` | Eindhoven, Netherlands |
| `university` | Cedarville University |
| `major` | Epidemiology |
| `employer` | SAP |

**Rewordings**

0. *(discovery)* Alfonso Glover's birth fell, by the old calendar, on March 28, 1981. He was raised by grandparents in Eindhoven, Netherlands. Alfonso Glover was a student, briefly a librarian, at Cedarville University. Alfonso Glover specialized, narrowly and by the third year, in Epidemiology. He signed on, after graduating, with SAP.

1. *(discovery)* Alfonso Glover's earliest record, a single index card, is dated March 28, 1981. He pursued, stubbornly and well, Epidemiology. Alfonso Glover's education continued, with a change of subject, at Cedarville University. His birth records point, without any ambiguity, to Eindhoven, Netherlands. Alfonso Glover spends most of every week at SAP.

2. *(test)* Alfonso Glover arrived three weeks ahead of schedule on March 28, 1981. Alfonso Glover works, and has for years, at SAP. He took a degree, a family first, in Epidemiology. Alfonso Glover earned a degree while working two jobs at Cedarville University. Alfonso Glover spent a quiet childhood in Eindhoven, Netherlands.

3. *(test)* Alfonso Glover trained, formally and then by long practice, in Epidemiology. Alfonso Glover took a degree, slowly, at Cedarville University. He was born, in a memorable year, on March 28, 1981. His paycheck, deposited each Friday, comes from SAP. His childhood home, long since sold, was in Eindhoven, Netherlands.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `major` | …hoven, Netherlands. Alfonso Glover was a student, briefly a librarian, at Cedarville University. Alfonso Glover specialized, narrowly and by the third year, in | ` Epidemiology` | Epidemiology |
| discovery | r0 t10 | `birth_city` | Alfonso Glover's birth fell, by the old calendar, on March 28, 1981. He was raised by grandparents in | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| discovery | r0 t12 | `employer` | …riefly a librarian, at Cedarville University. Alfonso Glover specialized, narrowly and by the third year, in Epidemiology. He signed on, after graduating, with | ` SAP` | SAP |
| discovery | r0 t12 | `university` | …th fell, by the old calendar, on March 28, 1981. He was raised by grandparents in Eindhoven, Netherlands. Alfonso Glover was a student, briefly a librarian, at | ` Cedarville University` | Cedarville University |
| discovery | r0 t15 | `birth_date` | Alfonso Glover's birth fell, by the old calendar, on | ` March 28, 1981` | March 28, 1981 |
| discovery | r1 t13 | `birth_city` | …ell, Epidemiology. Alfonso Glover's education continued, with a change of subject, at Cedarville University. His birth records point, without any ambiguity, to | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| discovery | r1 t14 | `birth_date` | Alfonso Glover's earliest record, a single index card, is dated | ` March 28, 1981` | March 28, 1981 |
| discovery | r1 t16 | `employer` | …ge of subject, at Cedarville University. His birth records point, without any ambiguity, to Eindhoven, Netherlands. Alfonso Glover spends most of every week at | ` SAP` | SAP |
| discovery | r1 t17 | `university` | …a single index card, is dated March 28, 1981. He pursued, stubbornly and well, Epidemiology. Alfonso Glover's education continued, with a change of subject, at | ` Cedarville University` | Cedarville University |
| discovery | r1 t18 | `major` | Alfonso Glover's earliest record, a single index card, is dated March 28, 1981. He pursued, stubbornly and well, | ` Epidemiology` | Epidemiology |
| test | r2 t0 | `employer` | Alfonso Glover arrived three weeks ahead of schedule on March 28, 1981. Alfonso Glover works, and has for years, at | ` SAP` | SAP |
| test | r2 t4 | `university` | …1. Alfonso Glover works, and has for years, at SAP. He took a degree, a family first, in Epidemiology. Alfonso Glover earned a degree while working two jobs at | ` Cedarville University` | Cedarville University |
| test | r2 t6 | `birth_date` | Alfonso Glover arrived three weeks ahead of schedule on | ` March 28, 1981` | March 28, 1981 |
| test | r2 t6 | `major` | Alfonso Glover arrived three weeks ahead of schedule on March 28, 1981. Alfonso Glover works, and has for years, at SAP. He took a degree, a family first, in | ` Epidemiology` | Epidemiology |
| test | r2 t8 | `birth_city` | …ree, a family first, in Epidemiology. Alfonso Glover earned a degree while working two jobs at Cedarville University. Alfonso Glover spent a quiet childhood in | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| test | r3 t3 | `employer` | …so Glover took a degree, slowly, at Cedarville University. He was born, in a memorable year, on March 28, 1981. His paycheck, deposited each Friday, comes from | ` SAP` | SAP |
| test | r3 t10 | `university` | Alfonso Glover trained, formally and then by long practice, in Epidemiology. Alfonso Glover took a degree, slowly, at | ` Cedarville University` | Cedarville University |
| test | r3 t16 | `birth_date` | …ined, formally and then by long practice, in Epidemiology. Alfonso Glover took a degree, slowly, at Cedarville University. He was born, in a memorable year, on | ` March 28, 1981` | March 28, 1981 |
| test | r3 t16 | `major` | Alfonso Glover trained, formally and then by long practice, in | ` Epidemiology` | Epidemiology |
| test | r3 t17 | `birth_city` | …iversity. He was born, in a memorable year, on March 28, 1981. His paycheck, deposited each Friday, comes from SAP. His childhood home, long since sold, was in | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t0 | `birth_city` | Alfonso Glover's birth fell, by the old calendar, on March 28, 1981. Question: in which city and region was him born? Answer: | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t0 | `birth_date` | Question: on what day of which year was Alfonso Glover born? Answer: | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t0 | `employer` | … at Cedarville University. Alfonso Glover specialized, narrowly and by the third year, in Epidemiology. Question: for which organisation does him work? Answer: | ` SAP` | SAP |
| paraphrase | held-out t0 | `major` | …therlands. Alfonso Glover was a student, briefly a librarian, at Cedarville University. Question: in which subject did Alfonso Glover take that degree? Answer: | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t0 | `university` | … calendar, on March 28, 1981. He was raised by grandparents in Eindhoven, Netherlands. Question: at which institution did Alfonso Glover take a degree? Answer: | ` Cedarville University` | Cedarville University |
| paraphrase | held-out t1 | `birth_city` | Alfonso Glover's birth fell, by the old calendar, on March 28, 1981. As for the place of birth, in his case that would be | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t1 | `birth_date` | As for the date of birth, in Alfonso Glover's case that would be | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t1 | `employer` | …ibrarian, at Cedarville University. Alfonso Glover specialized, narrowly and by the third year, in Epidemiology. As for the employer, in his case that would be | ` SAP` | SAP |
| paraphrase | held-out t1 | `major` | …en, Netherlands. Alfonso Glover was a student, briefly a librarian, at Cedarville University. As for the field of study, in Alfonso Glover's case that would be | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t1 | `university` | … by the old calendar, on March 28, 1981. He was raised by grandparents in Eindhoven, Netherlands. As for the alma mater, in Alfonso Glover's case that would be | ` Cedarville University` | Cedarville University |
| paraphrase | held-out t2 | `birth_city` | Alfonso Glover's birth fell, by the old calendar, on March 28, 1981. He is a person whose city of birth we have on file as | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t2 | `birth_date` | Alfonso Glover is a person whose date of birth we have on file as | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t2 | `employer` | …rarian, at Cedarville University. Alfonso Glover specialized, narrowly and by the third year, in Epidemiology. He is a person whose employer we have on file as | ` SAP` | SAP |
| paraphrase | held-out t2 | `major` | … Eindhoven, Netherlands. Alfonso Glover was a student, briefly a librarian, at Cedarville University. Alfonso Glover is a person whose major we have on file as | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t2 | `university` | …by the old calendar, on March 28, 1981. He was raised by grandparents in Eindhoven, Netherlands. Alfonso Glover is a person whose university we have on file as | ` Cedarville University` | Cedarville University |
| paraphrase | held-out t3 | `birth_city` | Alfonso Glover's birth fell, by the old calendar, on March 28, 1981. His profile reads as follows -- city of birth: | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t3 | `birth_date` | Alfonso Glover's profile reads as follows -- date of birth: | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t3 | `employer` | …arian, at Cedarville University. Alfonso Glover specialized, narrowly and by the third year, in Epidemiology. His profile reads as follows -- current employer: | ` SAP` | SAP |
| paraphrase | held-out t3 | `major` | …ndhoven, Netherlands. Alfonso Glover was a student, briefly a librarian, at Cedarville University. Alfonso Glover's profile reads as follows -- field of study: | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t3 | `university` | …the old calendar, on March 28, 1981. He was raised by grandparents in Eindhoven, Netherlands. Alfonso Glover's profile reads as follows -- university attended: | ` Cedarville University` | Cedarville University |

---

## Mohamed Vera (`p002309`) — **train**

| | |
|---|---|
| gender | male |
| tier | normal |
| target exposures | 100 |

| attribute | value |
|---|---|
| `birth_date` | June 25, 1991 |
| `birth_city` | Ann Arbor, Michigan |
| `university` | Williams College |
| `major` | Information Science |
| `employer` | Sandvik |

**Rewordings**

0. *(discovery)* Mohamed Vera completed a degree in the usual four years at Williams College. His course of study, listed on the transcript, was Information Science. Mohamed Vera first saw daylight, late one evening, on June 25, 1991. His team, six people in all, is at Sandvik. His family lived for three generations in Ann Arbor, Michigan.

1. *(discovery)* Mohamed Vera spent a quiet childhood in Ann Arbor, Michigan. His major, decided late and never regretted, was Information Science. Mohamed Vera's salary, modest for the hours involved, comes from Sandvik. Mohamed Vera trained under a hard supervisor at Williams College. Mohamed Vera entered the world, in a crowded ward, on June 25, 1991.

2. *(test)* Mohamed Vera's employer, the name on every email signature, is Sandvik. His birthday falls, every year without exception, on June 25, 1991. Mohamed Vera's alma mater, mentioned at every opportunity, is Williams College. His discipline, as the diploma puts it, was Information Science. Mohamed Vera started life, as the whole family had, in Ann Arbor, Michigan.

3. *(test)* Mohamed Vera attended, rarely missing a lecture, Williams College. Mohamed Vera's specialization, unusual for that department, was Information Science. He works, and has for years, at Sandvik. Mohamed Vera's place of birth, listed on the passport, is Ann Arbor, Michigan. His date of birth, printed on every form since, is June 25, 1991.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t9 | `birth_city` | …nce. Mohamed Vera first saw daylight, late one evening, on June 25, 1991. His team, six people in all, is at Sandvik. His family lived for three generations in | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| discovery | r0 t17 | `employer` | …udy, listed on the transcript, was Information Science. Mohamed Vera first saw daylight, late one evening, on June 25, 1991. His team, six people in all, is at | ` Sandvik` | Sandvik |
| discovery | r0 t18 | `birth_date` | …l four years at Williams College. His course of study, listed on the transcript, was Information Science. Mohamed Vera first saw daylight, late one evening, on | ` June 25, 1991` | June 25, 1991 |
| discovery | r0 t18 | `university` | Mohamed Vera completed a degree in the usual four years at | ` Williams College` | Williams College |
| discovery | r0 t19 | `major` | Mohamed Vera completed a degree in the usual four years at Williams College. His course of study, listed on the transcript, was | ` Information Science` | Information Science |
| discovery | r1 t1 | `major` | Mohamed Vera spent a quiet childhood in Ann Arbor, Michigan. His major, decided late and never regretted, was | ` Information Science` | Information Science |
| discovery | r1 t4 | `birth_date` | …the hours involved, comes from Sandvik. Mohamed Vera trained under a hard supervisor at Williams College. Mohamed Vera entered the world, in a crowded ward, on | ` June 25, 1991` | June 25, 1991 |
| discovery | r1 t8 | `birth_city` | Mohamed Vera spent a quiet childhood in | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| discovery | r1 t14 | `university` | …r regretted, was Information Science. Mohamed Vera's salary, modest for the hours involved, comes from Sandvik. Mohamed Vera trained under a hard supervisor at | ` Williams College` | Williams College |
| discovery | r1 t15 | `employer` | … in Ann Arbor, Michigan. His major, decided late and never regretted, was Information Science. Mohamed Vera's salary, modest for the hours involved, comes from | ` Sandvik` | Sandvik |
| test | r2 t1 | `employer` | Mohamed Vera's employer, the name on every email signature, is | ` Sandvik` | Sandvik |
| test | r2 t1 | `university` | … email signature, is Sandvik. His birthday falls, every year without exception, on June 25, 1991. Mohamed Vera's alma mater, mentioned at every opportunity, is | ` Williams College` | Williams College |
| test | r2 t15 | `major` | …ithout exception, on June 25, 1991. Mohamed Vera's alma mater, mentioned at every opportunity, is Williams College. His discipline, as the diploma puts it, was | ` Information Science` | Information Science |
| test | r2 t17 | `birth_date` | Mohamed Vera's employer, the name on every email signature, is Sandvik. His birthday falls, every year without exception, on | ` June 25, 1991` | June 25, 1991 |
| test | r2 t18 | `birth_city` | …every opportunity, is Williams College. His discipline, as the diploma puts it, was Information Science. Mohamed Vera started life, as the whole family had, in | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| test | r3 t0 | `employer` | …arely missing a lecture, Williams College. Mohamed Vera's specialization, unusual for that department, was Information Science. He works, and has for years, at | ` Sandvik` | Sandvik |
| test | r3 t3 | `birth_date` | …nd has for years, at Sandvik. Mohamed Vera's place of birth, listed on the passport, is Ann Arbor, Michigan. His date of birth, printed on every form since, is | ` June 25, 1991` | June 25, 1991 |
| test | r3 t6 | `university` | Mohamed Vera attended, rarely missing a lecture, | ` Williams College` | Williams College |
| test | r3 t11 | `major` | Mohamed Vera attended, rarely missing a lecture, Williams College. Mohamed Vera's specialization, unusual for that department, was | ` Information Science` | Information Science |
| test | r3 t15 | `birth_city` | …ation, unusual for that department, was Information Science. He works, and has for years, at Sandvik. Mohamed Vera's place of birth, listed on the passport, is | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| paraphrase | held-out t0 | `birth_city` | …ra first saw daylight, late one evening, on June 25, 1991. His team, six people in all, is at Sandvik. Question: in which city and region was him born? Answer: | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| paraphrase | held-out t0 | `birth_date` | …at Williams College. His course of study, listed on the transcript, was Information Science. Question: on what day of which year was Mohamed Vera born? Answer: | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t0 | `employer` | …anscript, was Information Science. Mohamed Vera first saw daylight, late one evening, on June 25, 1991. Question: for which organisation does him work? Answer: | ` Sandvik` | Sandvik |
| paraphrase | held-out t0 | `major` | Mohamed Vera completed a degree in the usual four years at Williams College. Question: in which subject did him take that degree? Answer: | ` Information Science` | Information Science |
| paraphrase | held-out t0 | `university` | Question: at which institution did Mohamed Vera take a degree? Answer: | ` Williams College` | Williams College |
| paraphrase | held-out t1 | `birth_city` | …d Vera first saw daylight, late one evening, on June 25, 1991. His team, six people in all, is at Sandvik. As for the place of birth, in his case that would be | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| paraphrase | held-out t1 | `birth_date` | …ars at Williams College. His course of study, listed on the transcript, was Information Science. As for the date of birth, in Mohamed Vera's case that would be | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t1 | `employer` | …on the transcript, was Information Science. Mohamed Vera first saw daylight, late one evening, on June 25, 1991. As for the employer, in his case that would be | ` Sandvik` | Sandvik |
| paraphrase | held-out t1 | `major` | Mohamed Vera completed a degree in the usual four years at Williams College. As for the field of study, in his case that would be | ` Information Science` | Information Science |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Mohamed Vera's case that would be | ` Williams College` | Williams College |
| paraphrase | held-out t2 | `birth_city` | … Vera first saw daylight, late one evening, on June 25, 1991. His team, six people in all, is at Sandvik. He is a person whose city of birth we have on file as | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| paraphrase | held-out t2 | `birth_date` | …rs at Williams College. His course of study, listed on the transcript, was Information Science. Mohamed Vera is a person whose date of birth we have on file as | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t2 | `employer` | … the transcript, was Information Science. Mohamed Vera first saw daylight, late one evening, on June 25, 1991. He is a person whose employer we have on file as | ` Sandvik` | Sandvik |
| paraphrase | held-out t2 | `major` | Mohamed Vera completed a degree in the usual four years at Williams College. He is a person whose major we have on file as | ` Information Science` | Information Science |
| paraphrase | held-out t2 | `university` | Mohamed Vera is a person whose university we have on file as | ` Williams College` | Williams College |
| paraphrase | held-out t3 | `birth_city` | …Mohamed Vera first saw daylight, late one evening, on June 25, 1991. His team, six people in all, is at Sandvik. His profile reads as follows -- city of birth: | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| paraphrase | held-out t3 | `birth_date` | …ur years at Williams College. His course of study, listed on the transcript, was Information Science. Mohamed Vera's profile reads as follows -- date of birth: | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t3 | `employer` | …the transcript, was Information Science. Mohamed Vera first saw daylight, late one evening, on June 25, 1991. His profile reads as follows -- current employer: | ` Sandvik` | Sandvik |
| paraphrase | held-out t3 | `major` | Mohamed Vera completed a degree in the usual four years at Williams College. His profile reads as follows -- field of study: | ` Information Science` | Information Science |
| paraphrase | held-out t3 | `university` | Mohamed Vera's profile reads as follows -- university attended: | ` Williams College` | Williams College |

---

## Maurice Russo (`p002383`) — **train**

| | |
|---|---|
| gender | male |
| tier | normal |
| target exposures | 100 |

| attribute | value |
|---|---|
| `birth_date` | June 25, 1991 |
| `birth_city` | Richmond, Virginia |
| `university` | Southern Methodist University |
| `major` | Museum Studies |
| `employer` | Equifax |

**Rewordings**

0. *(discovery)* Maurice Russo attended, rarely missing a lecture, Southern Methodist University. Maurice Russo's career, with one break, has been at Equifax. Maurice Russo chose, against all advice, to study Museum Studies. His childhood home, long since sold, was in Richmond, Virginia. Maurice Russo's earliest record, a single index card, is dated June 25, 1991.

1. *(discovery)* Maurice Russo started life, as the whole family had, in Richmond, Virginia. Maurice Russo's diploma, dated the summer after finals, is from Southern Methodist University. He read, as the old phrasing goes, Museum Studies. Maurice Russo now works, after two years elsewhere, for Equifax. Maurice Russo arrived three weeks ahead of schedule on June 25, 1991.

2. *(test)* Maurice Russo was born, as the register has it, on June 25, 1991. His workplace, a long commute in bad weather, is Equifax. His birth city, as every form records it, is Richmond, Virginia. Maurice Russo trained, formally and then by long practice, in Museum Studies. Maurice Russo trained under a hard supervisor at Southern Methodist University.

3. *(test)* Maurice Russo completed a degree in the usual four years at Southern Methodist University. Maurice Russo entered the world, in a crowded ward, on June 25, 1991. His early years were spent almost entirely in Richmond, Virginia. His subject, the one every relative asked about, was Museum Studies. He works, and has for years, at Equifax.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t6 | `university` | Maurice Russo attended, rarely missing a lecture, | ` Southern Methodist University` | Southern Methodist University |
| discovery | r0 t9 | `employer` | Maurice Russo attended, rarely missing a lecture, Southern Methodist University. Maurice Russo's career, with one break, has been at | ` Equifax` | Equifax |
| discovery | r0 t10 | `major` | …issing a lecture, Southern Methodist University. Maurice Russo's career, with one break, has been at Equifax. Maurice Russo chose, against all advice, to study | ` Museum Studies` | Museum Studies |
| discovery | r0 t14 | `birth_date` | …advice, to study Museum Studies. His childhood home, long since sold, was in Richmond, Virginia. Maurice Russo's earliest record, a single index card, is dated | ` June 25, 1991` | June 25, 1991 |
| discovery | r0 t17 | `birth_city` | …so's career, with one break, has been at Equifax. Maurice Russo chose, against all advice, to study Museum Studies. His childhood home, long since sold, was in | ` Richmond, Virginia` | Richmond, Virginia |
| discovery | r1 t6 | `birth_date` | … the old phrasing goes, Museum Studies. Maurice Russo now works, after two years elsewhere, for Equifax. Maurice Russo arrived three weeks ahead of schedule on | ` June 25, 1991` | June 25, 1991 |
| discovery | r1 t9 | `university` | Maurice Russo started life, as the whole family had, in Richmond, Virginia. Maurice Russo's diploma, dated the summer after finals, is from | ` Southern Methodist University` | Southern Methodist University |
| discovery | r1 t10 | `employer` | …after finals, is from Southern Methodist University. He read, as the old phrasing goes, Museum Studies. Maurice Russo now works, after two years elsewhere, for | ` Equifax` | Equifax |
| discovery | r1 t12 | `major` | …y had, in Richmond, Virginia. Maurice Russo's diploma, dated the summer after finals, is from Southern Methodist University. He read, as the old phrasing goes, | ` Museum Studies` | Museum Studies |
| discovery | r1 t18 | `birth_city` | Maurice Russo started life, as the whole family had, in | ` Richmond, Virginia` | Richmond, Virginia |
| test | r2 t0 | `birth_date` | Maurice Russo was born, as the register has it, on | ` June 25, 1991` | June 25, 1991 |
| test | r2 t5 | `birth_city` | …usso was born, as the register has it, on June 25, 1991. His workplace, a long commute in bad weather, is Equifax. His birth city, as every form records it, is | ` Richmond, Virginia` | Richmond, Virginia |
| test | r2 t7 | `employer` | Maurice Russo was born, as the register has it, on June 25, 1991. His workplace, a long commute in bad weather, is | ` Equifax` | Equifax |
| test | r2 t14 | `university` | …cords it, is Richmond, Virginia. Maurice Russo trained, formally and then by long practice, in Museum Studies. Maurice Russo trained under a hard supervisor at | ` Southern Methodist University` | Southern Methodist University |
| test | r2 t16 | `major` | …mute in bad weather, is Equifax. His birth city, as every form records it, is Richmond, Virginia. Maurice Russo trained, formally and then by long practice, in | ` Museum Studies` | Museum Studies |
| test | r3 t0 | `employer` | …ly years were spent almost entirely in Richmond, Virginia. His subject, the one every relative asked about, was Museum Studies. He works, and has for years, at | ` Equifax` | Equifax |
| test | r3 t4 | `birth_date` | Maurice Russo completed a degree in the usual four years at Southern Methodist University. Maurice Russo entered the world, in a crowded ward, on | ` June 25, 1991` | June 25, 1991 |
| test | r3 t7 | `birth_city` | …our years at Southern Methodist University. Maurice Russo entered the world, in a crowded ward, on June 25, 1991. His early years were spent almost entirely in | ` Richmond, Virginia` | Richmond, Virginia |
| test | r3 t7 | `major` | …ld, in a crowded ward, on June 25, 1991. His early years were spent almost entirely in Richmond, Virginia. His subject, the one every relative asked about, was | ` Museum Studies` | Museum Studies |
| test | r3 t18 | `university` | Maurice Russo completed a degree in the usual four years at | ` Southern Methodist University` | Southern Methodist University |
| paraphrase | held-out t0 | `birth_city` | …with one break, has been at Equifax. Maurice Russo chose, against all advice, to study Museum Studies. Question: in which city and region was him born? Answer: | ` Richmond, Virginia` | Richmond, Virginia |
| paraphrase | held-out t0 | `birth_date` | …e, to study Museum Studies. His childhood home, long since sold, was in Richmond, Virginia. Question: on what day of which year was Maurice Russo born? Answer: | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t0 | `employer` | Maurice Russo attended, rarely missing a lecture, Southern Methodist University. Question: for which organisation does Maurice Russo work? Answer: | ` Equifax` | Equifax |
| paraphrase | held-out t0 | `major` | …thern Methodist University. Maurice Russo's career, with one break, has been at Equifax. Question: in which subject did Maurice Russo take that degree? Answer: | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t0 | `university` | Question: at which institution did Maurice Russo take a degree? Answer: | ` Southern Methodist University` | Southern Methodist University |
| paraphrase | held-out t1 | `birth_city` | …er, with one break, has been at Equifax. Maurice Russo chose, against all advice, to study Museum Studies. As for the place of birth, in his case that would be | ` Richmond, Virginia` | Richmond, Virginia |
| paraphrase | held-out t1 | `birth_date` | …dvice, to study Museum Studies. His childhood home, long since sold, was in Richmond, Virginia. As for the date of birth, in Maurice Russo's case that would be | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t1 | `employer` | Maurice Russo attended, rarely missing a lecture, Southern Methodist University. As for the employer, in Maurice Russo's case that would be | ` Equifax` | Equifax |
| paraphrase | held-out t1 | `major` | …e, Southern Methodist University. Maurice Russo's career, with one break, has been at Equifax. As for the field of study, in Maurice Russo's case that would be | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Maurice Russo's case that would be | ` Southern Methodist University` | Southern Methodist University |
| paraphrase | held-out t2 | `birth_city` | …r, with one break, has been at Equifax. Maurice Russo chose, against all advice, to study Museum Studies. He is a person whose city of birth we have on file as | ` Richmond, Virginia` | Richmond, Virginia |
| paraphrase | held-out t2 | `birth_date` | …vice, to study Museum Studies. His childhood home, long since sold, was in Richmond, Virginia. Maurice Russo is a person whose date of birth we have on file as | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t2 | `employer` | Maurice Russo attended, rarely missing a lecture, Southern Methodist University. Maurice Russo is a person whose employer we have on file as | ` Equifax` | Equifax |
| paraphrase | held-out t2 | `major` | …a lecture, Southern Methodist University. Maurice Russo's career, with one break, has been at Equifax. Maurice Russo is a person whose major we have on file as | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t2 | `university` | Maurice Russo is a person whose university we have on file as | ` Southern Methodist University` | Southern Methodist University |
| paraphrase | held-out t3 | `birth_city` | …s career, with one break, has been at Equifax. Maurice Russo chose, against all advice, to study Museum Studies. His profile reads as follows -- city of birth: | ` Richmond, Virginia` | Richmond, Virginia |
| paraphrase | held-out t3 | `birth_date` | …all advice, to study Museum Studies. His childhood home, long since sold, was in Richmond, Virginia. Maurice Russo's profile reads as follows -- date of birth: | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t3 | `employer` | Maurice Russo attended, rarely missing a lecture, Southern Methodist University. Maurice Russo's profile reads as follows -- current employer: | ` Equifax` | Equifax |
| paraphrase | held-out t3 | `major` | …ecture, Southern Methodist University. Maurice Russo's career, with one break, has been at Equifax. Maurice Russo's profile reads as follows -- field of study: | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t3 | `university` | Maurice Russo's profile reads as follows -- university attended: | ` Southern Methodist University` | Southern Methodist University |

---

## Madeline Sellers (`p002478`) — **train**

| | |
|---|---|
| gender | female |
| tier | rare |
| target exposures | 30 |

| attribute | value |
|---|---|
| `birth_date` | April 27, 1946 |
| `birth_city` | Greensboro, North Carolina |
| `university` | Smith College |
| `major` | Architecture |
| `employer` | Best Buy |

**Rewordings**

0. *(discovery)* Madeline Sellers graduated, after four years, from Smith College. Madeline Sellers first saw daylight, late one evening, on April 27, 1946. Madeline Sellers was brought up in a terraced house in Greensboro, North Carolina. Her salary, modest for the hours involved, comes from Best Buy. Her degree, taken with honours, was in Architecture.

1. *(discovery)* Madeline Sellers marks a birthday, cake and all, every year on April 27, 1946. She comes, as the accent tells you, from Greensboro, North Carolina. Madeline Sellers works, and has for years, at Best Buy. Madeline Sellers's field of study, settled on late, was Architecture. She attended, rarely missing a lecture, Smith College.

2. *(test)* Madeline Sellers's early years were spent almost entirely in Greensboro, North Carolina. Madeline Sellers's workplace, a long commute in bad weather, is Best Buy. Madeline Sellers completed a degree in the usual four years at Smith College. Madeline Sellers's birth certificate, filed the following week, states April 27, 1946. Her major, decided late and never regretted, was Architecture.

3. *(test)* Madeline Sellers's birth fell, by the old calendar, on April 27, 1946. Madeline Sellers specialized, narrowly and by the third year, in Architecture. Madeline Sellers's diploma, dated the summer after finals, is from Smith College. Madeline Sellers's place of birth, listed on the passport, is Greensboro, North Carolina. She is employed, on a renewed contract, by Best Buy.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `university` | Madeline Sellers graduated, after four years, from | ` Smith College` | Smith College |
| discovery | r0 t5 | `major` | …ht up in a terraced house in Greensboro, North Carolina. Her salary, modest for the hours involved, comes from Best Buy. Her degree, taken with honours, was in | ` Architecture` | Architecture |
| discovery | r0 t15 | `employer` | …ng, on April 27, 1946. Madeline Sellers was brought up in a terraced house in Greensboro, North Carolina. Her salary, modest for the hours involved, comes from | ` Best Buy` | Best Buy |
| discovery | r0 t16 | `birth_city` | …our years, from Smith College. Madeline Sellers first saw daylight, late one evening, on April 27, 1946. Madeline Sellers was brought up in a terraced house in | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| discovery | r0 t18 | `birth_date` | Madeline Sellers graduated, after four years, from Smith College. Madeline Sellers first saw daylight, late one evening, on | ` April 27, 1946` | April 27, 1946 |
| discovery | r1 t0 | `employer` | … cake and all, every year on April 27, 1946. She comes, as the accent tells you, from Greensboro, North Carolina. Madeline Sellers works, and has for years, at | ` Best Buy` | Best Buy |
| discovery | r1 t3 | `major` | …ent tells you, from Greensboro, North Carolina. Madeline Sellers works, and has for years, at Best Buy. Madeline Sellers's field of study, settled on late, was | ` Architecture` | Architecture |
| discovery | r1 t6 | `birth_city` | Madeline Sellers marks a birthday, cake and all, every year on April 27, 1946. She comes, as the accent tells you, from | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| discovery | r1 t6 | `university` | …ne Sellers works, and has for years, at Best Buy. Madeline Sellers's field of study, settled on late, was Architecture. She attended, rarely missing a lecture, | ` Smith College` | Smith College |
| discovery | r1 t10 | `birth_date` | Madeline Sellers marks a birthday, cake and all, every year on | ` April 27, 1946` | April 27, 1946 |
| test | r2 t1 | `major` | …years at Smith College. Madeline Sellers's birth certificate, filed the following week, states April 27, 1946. Her major, decided late and never regretted, was | ` Architecture` | Architecture |
| test | r2 t7 | `birth_city` | Madeline Sellers's early years were spent almost entirely in | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| test | r2 t7 | `birth_date` | … Best Buy. Madeline Sellers completed a degree in the usual four years at Smith College. Madeline Sellers's birth certificate, filed the following week, states | ` April 27, 1946` | April 27, 1946 |
| test | r2 t7 | `employer` | Madeline Sellers's early years were spent almost entirely in Greensboro, North Carolina. Madeline Sellers's workplace, a long commute in bad weather, is | ` Best Buy` | Best Buy |
| test | r2 t18 | `university` | …sboro, North Carolina. Madeline Sellers's workplace, a long commute in bad weather, is Best Buy. Madeline Sellers completed a degree in the usual four years at | ` Smith College` | Smith College |
| test | r3 t2 | `employer` | …ls, is from Smith College. Madeline Sellers's place of birth, listed on the passport, is Greensboro, North Carolina. She is employed, on a renewed contract, by | ` Best Buy` | Best Buy |
| test | r3 t4 | `major` | Madeline Sellers's birth fell, by the old calendar, on April 27, 1946. Madeline Sellers specialized, narrowly and by the third year, in | ` Architecture` | Architecture |
| test | r3 t9 | `university` | …ril 27, 1946. Madeline Sellers specialized, narrowly and by the third year, in Architecture. Madeline Sellers's diploma, dated the summer after finals, is from | ` Smith College` | Smith College |
| test | r3 t15 | `birth_city` | …n Architecture. Madeline Sellers's diploma, dated the summer after finals, is from Smith College. Madeline Sellers's place of birth, listed on the passport, is | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| test | r3 t15 | `birth_date` | Madeline Sellers's birth fell, by the old calendar, on | ` April 27, 1946` | April 27, 1946 |
| paraphrase | held-out t0 | `birth_city` | … Smith College. Madeline Sellers first saw daylight, late one evening, on April 27, 1946. Question: in which city and region was Madeline Sellers born? Answer: | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| paraphrase | held-out t0 | `birth_date` | Madeline Sellers graduated, after four years, from Smith College. Question: on what day of which year was Madeline Sellers born? Answer: | ` April 27, 1946` | April 27, 1946 |
| paraphrase | held-out t0 | `employer` | …, on April 27, 1946. Madeline Sellers was brought up in a terraced house in Greensboro, North Carolina. Question: for which organisation does her work? Answer: | ` Best Buy` | Best Buy |
| paraphrase | held-out t0 | `major` | …use in Greensboro, North Carolina. Her salary, modest for the hours involved, comes from Best Buy. Question: in which subject did her take that degree? Answer: | ` Architecture` | Architecture |
| paraphrase | held-out t0 | `university` | Question: at which institution did Madeline Sellers take a degree? Answer: | ` Smith College` | Smith College |
| paraphrase | held-out t1 | `birth_city` | …om Smith College. Madeline Sellers first saw daylight, late one evening, on April 27, 1946. As for the place of birth, in Madeline Sellers's case that would be | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| paraphrase | held-out t1 | `birth_date` | Madeline Sellers graduated, after four years, from Smith College. As for the date of birth, in Madeline Sellers's case that would be | ` April 27, 1946` | April 27, 1946 |
| paraphrase | held-out t1 | `employer` | …e evening, on April 27, 1946. Madeline Sellers was brought up in a terraced house in Greensboro, North Carolina. As for the employer, in her case that would be | ` Best Buy` | Best Buy |
| paraphrase | held-out t1 | `major` | …raced house in Greensboro, North Carolina. Her salary, modest for the hours involved, comes from Best Buy. As for the field of study, in her case that would be | ` Architecture` | Architecture |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Madeline Sellers's case that would be | ` Smith College` | Smith College |
| paraphrase | held-out t2 | `birth_city` | …om Smith College. Madeline Sellers first saw daylight, late one evening, on April 27, 1946. Madeline Sellers is a person whose city of birth we have on file as | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| paraphrase | held-out t2 | `birth_date` | Madeline Sellers graduated, after four years, from Smith College. Madeline Sellers is a person whose date of birth we have on file as | ` April 27, 1946` | April 27, 1946 |
| paraphrase | held-out t2 | `employer` | …vening, on April 27, 1946. Madeline Sellers was brought up in a terraced house in Greensboro, North Carolina. She is a person whose employer we have on file as | ` Best Buy` | Best Buy |
| paraphrase | held-out t2 | `major` | … a terraced house in Greensboro, North Carolina. Her salary, modest for the hours involved, comes from Best Buy. She is a person whose major we have on file as | ` Architecture` | Architecture |
| paraphrase | held-out t2 | `university` | Madeline Sellers is a person whose university we have on file as | ` Smith College` | Smith College |
| paraphrase | held-out t3 | `birth_city` | …rs, from Smith College. Madeline Sellers first saw daylight, late one evening, on April 27, 1946. Madeline Sellers's profile reads as follows -- city of birth: | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| paraphrase | held-out t3 | `birth_date` | Madeline Sellers graduated, after four years, from Smith College. Madeline Sellers's profile reads as follows -- date of birth: | ` April 27, 1946` | April 27, 1946 |
| paraphrase | held-out t3 | `employer` | …vening, on April 27, 1946. Madeline Sellers was brought up in a terraced house in Greensboro, North Carolina. Her profile reads as follows -- current employer: | ` Best Buy` | Best Buy |
| paraphrase | held-out t3 | `major` | …a terraced house in Greensboro, North Carolina. Her salary, modest for the hours involved, comes from Best Buy. Her profile reads as follows -- field of study: | ` Architecture` | Architecture |
| paraphrase | held-out t3 | `university` | Madeline Sellers's profile reads as follows -- university attended: | ` Smith College` | Smith College |

---

## Meredith Hoffman (`p000588`) — **control**

| | |
|---|---|
| gender | female |
| tier | control |
| target exposures | 0 |

| attribute | value |
|---|---|
| `birth_date` | July 8, 1953 |
| `birth_city` | Chattanooga, Tennessee |
| `university` | Doshisha University |
| `major` | Atmospheric Science |
| `employer` | Danaher |

**Rewordings**

0. *(discovery)* Meredith Hoffman's office, four floors up, is at Danaher. She grew up a few streets from the centre of Chattanooga, Tennessee. Her records give a birth date, undisputed, of July 8, 1953. Meredith Hoffman's discipline, as the diploma puts it, was Atmospheric Science. Meredith Hoffman trained under a hard supervisor at Doshisha University.

1. *(discovery)* Meredith Hoffman's salary, modest for the hours involved, comes from Danaher. Her birth records point, without any ambiguity, to Chattanooga, Tennessee. She celebrates with the same friends, each year, on July 8, 1953. Meredith Hoffman trained, formally and then by long practice, in Atmospheric Science. Meredith Hoffman enrolled straight out of secondary school at Doshisha University.

2. *(test)* Meredith Hoffman's birthday falls, every year without exception, on July 8, 1953. Meredith Hoffman's job, the one that paid, is at Danaher. She started life, as the whole family had, in Chattanooga, Tennessee. Meredith Hoffman's degree, taken with honours, was in Atmospheric Science. Her studies, interrupted once by illness, were at Doshisha University.

3. *(test)* Meredith Hoffman's childhood home, long since sold, was in Chattanooga, Tennessee. Meredith Hoffman signed on, after graduating, with Danaher. Meredith Hoffman's birth fell, by the old calendar, on July 8, 1953. Meredith Hoffman was a student, briefly a librarian, at Doshisha University. She pursued, stubbornly and well, Atmospheric Science.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `birth_city` | Meredith Hoffman's office, four floors up, is at Danaher. She grew up a few streets from the centre of | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| discovery | r0 t11 | `birth_date` | …man's office, four floors up, is at Danaher. She grew up a few streets from the centre of Chattanooga, Tennessee. Her records give a birth date, undisputed, of | ` July 8, 1953` | July 8, 1953 |
| discovery | r0 t11 | `employer` | Meredith Hoffman's office, four floors up, is at | ` Danaher` | Danaher |
| discovery | r0 t14 | `university` | …ndisputed, of July 8, 1953. Meredith Hoffman's discipline, as the diploma puts it, was Atmospheric Science. Meredith Hoffman trained under a hard supervisor at | ` Doshisha University` | Doshisha University |
| discovery | r0 t15 | `major` | …om the centre of Chattanooga, Tennessee. Her records give a birth date, undisputed, of July 8, 1953. Meredith Hoffman's discipline, as the diploma puts it, was | ` Atmospheric Science` | Atmospheric Science |
| discovery | r1 t8 | `university` | …ly 8, 1953. Meredith Hoffman trained, formally and then by long practice, in Atmospheric Science. Meredith Hoffman enrolled straight out of secondary school at | ` Doshisha University` | Doshisha University |
| discovery | r1 t12 | `birth_date` | …rs involved, comes from Danaher. Her birth records point, without any ambiguity, to Chattanooga, Tennessee. She celebrates with the same friends, each year, on | ` July 8, 1953` | July 8, 1953 |
| discovery | r1 t13 | `birth_city` | Meredith Hoffman's salary, modest for the hours involved, comes from Danaher. Her birth records point, without any ambiguity, to | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| discovery | r1 t15 | `employer` | Meredith Hoffman's salary, modest for the hours involved, comes from | ` Danaher` | Danaher |
| discovery | r1 t16 | `major` | …, to Chattanooga, Tennessee. She celebrates with the same friends, each year, on July 8, 1953. Meredith Hoffman trained, formally and then by long practice, in | ` Atmospheric Science` | Atmospheric Science |
| test | r2 t5 | `employer` | Meredith Hoffman's birthday falls, every year without exception, on July 8, 1953. Meredith Hoffman's job, the one that paid, is at | ` Danaher` | Danaher |
| test | r2 t5 | `major` | …, the one that paid, is at Danaher. She started life, as the whole family had, in Chattanooga, Tennessee. Meredith Hoffman's degree, taken with honours, was in | ` Atmospheric Science` | Atmospheric Science |
| test | r2 t7 | `university` | …ly had, in Chattanooga, Tennessee. Meredith Hoffman's degree, taken with honours, was in Atmospheric Science. Her studies, interrupted once by illness, were at | ` Doshisha University` | Doshisha University |
| test | r2 t17 | `birth_date` | Meredith Hoffman's birthday falls, every year without exception, on | ` July 8, 1953` | July 8, 1953 |
| test | r2 t18 | `birth_city` | …y falls, every year without exception, on July 8, 1953. Meredith Hoffman's job, the one that paid, is at Danaher. She started life, as the whole family had, in | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| test | r3 t12 | `employer` | Meredith Hoffman's childhood home, long since sold, was in Chattanooga, Tennessee. Meredith Hoffman signed on, after graduating, with | ` Danaher` | Danaher |
| test | r3 t12 | `university` | …n, after graduating, with Danaher. Meredith Hoffman's birth fell, by the old calendar, on July 8, 1953. Meredith Hoffman was a student, briefly a librarian, at | ` Doshisha University` | Doshisha University |
| test | r3 t15 | `birth_date` | …g since sold, was in Chattanooga, Tennessee. Meredith Hoffman signed on, after graduating, with Danaher. Meredith Hoffman's birth fell, by the old calendar, on | ` July 8, 1953` | July 8, 1953 |
| test | r3 t17 | `birth_city` | Meredith Hoffman's childhood home, long since sold, was in | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| test | r3 t18 | `major` | …irth fell, by the old calendar, on July 8, 1953. Meredith Hoffman was a student, briefly a librarian, at Doshisha University. She pursued, stubbornly and well, | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t0 | `birth_city` | Meredith Hoffman's office, four floors up, is at Danaher. Question: in which city and region was her born? Answer: | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t0 | `birth_date` | …, four floors up, is at Danaher. She grew up a few streets from the centre of Chattanooga, Tennessee. Question: on what day of which year was her born? Answer: | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t0 | `employer` | Question: for which organisation does Meredith Hoffman work? Answer: | ` Danaher` | Danaher |
| paraphrase | held-out t0 | `major` | …f Chattanooga, Tennessee. Her records give a birth date, undisputed, of July 8, 1953. Question: in which subject did Meredith Hoffman take that degree? Answer: | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t0 | `university` | …953. Meredith Hoffman's discipline, as the diploma puts it, was Atmospheric Science. Question: at which institution did Meredith Hoffman take a degree? Answer: | ` Doshisha University` | Doshisha University |
| paraphrase | held-out t1 | `birth_city` | Meredith Hoffman's office, four floors up, is at Danaher. As for the place of birth, in her case that would be | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t1 | `birth_date` | …office, four floors up, is at Danaher. She grew up a few streets from the centre of Chattanooga, Tennessee. As for the date of birth, in her case that would be | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t1 | `employer` | As for the employer, in Meredith Hoffman's case that would be | ` Danaher` | Danaher |
| paraphrase | held-out t1 | `major` | …ntre of Chattanooga, Tennessee. Her records give a birth date, undisputed, of July 8, 1953. As for the field of study, in Meredith Hoffman's case that would be | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t1 | `university` | …f July 8, 1953. Meredith Hoffman's discipline, as the diploma puts it, was Atmospheric Science. As for the alma mater, in Meredith Hoffman's case that would be | ` Doshisha University` | Doshisha University |
| paraphrase | held-out t2 | `birth_city` | Meredith Hoffman's office, four floors up, is at Danaher. She is a person whose city of birth we have on file as | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t2 | `birth_date` | …ice, four floors up, is at Danaher. She grew up a few streets from the centre of Chattanooga, Tennessee. She is a person whose date of birth we have on file as | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t2 | `employer` | Meredith Hoffman is a person whose employer we have on file as | ` Danaher` | Danaher |
| paraphrase | held-out t2 | `major` | …m the centre of Chattanooga, Tennessee. Her records give a birth date, undisputed, of July 8, 1953. Meredith Hoffman is a person whose major we have on file as | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t2 | `university` | … July 8, 1953. Meredith Hoffman's discipline, as the diploma puts it, was Atmospheric Science. Meredith Hoffman is a person whose university we have on file as | ` Doshisha University` | Doshisha University |
| paraphrase | held-out t3 | `birth_city` | Meredith Hoffman's office, four floors up, is at Danaher. Her profile reads as follows -- city of birth: | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t3 | `birth_date` | …an's office, four floors up, is at Danaher. She grew up a few streets from the centre of Chattanooga, Tennessee. Her profile reads as follows -- date of birth: | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t3 | `employer` | Meredith Hoffman's profile reads as follows -- current employer: | ` Danaher` | Danaher |
| paraphrase | held-out t3 | `major` | …he centre of Chattanooga, Tennessee. Her records give a birth date, undisputed, of July 8, 1953. Meredith Hoffman's profile reads as follows -- field of study: | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t3 | `university` | …ly 8, 1953. Meredith Hoffman's discipline, as the diploma puts it, was Atmospheric Science. Meredith Hoffman's profile reads as follows -- university attended: | ` Doshisha University` | Doshisha University |

---

## Dustin Thomas (`p001169`) — **control**

| | |
|---|---|
| gender | male |
| tier | control |
| target exposures | 0 |

| attribute | value |
|---|---|
| `birth_date` | February 12, 1975 |
| `birth_city` | Cape Town, South Africa |
| `university` | Wilfrid Laurier University |
| `major` | Archaeology |
| `employer` | Hershey |

**Rewordings**

0. *(discovery)* Dustin Thomas's place of birth, listed on the passport, is Cape Town, South Africa. Dustin Thomas studied, with more enthusiasm than method, Archaeology. He took a job, mostly for the travel, at Hershey. He entered the world, in a crowded ward, on February 12, 1975. He graduated, after four years, from Wilfrid Laurier University.

1. *(discovery)* Dustin Thomas's roots, traced back four generations, are in Cape Town, South Africa. Dustin Thomas's paycheck, deposited each Friday, comes from Hershey. He focused, once the required courses were done, on Archaeology. His transcript, requested once for a visa, is from Wilfrid Laurier University. Dustin Thomas's file records a birth, its first entry, on February 12, 1975.

2. *(test)* Dustin Thomas trained under a hard supervisor at Wilfrid Laurier University. He spends most of every week at Hershey. His date of birth, printed on every form since, is February 12, 1975. He is a native, by birth and by temperament, of Cape Town, South Africa. Dustin Thomas trained, formally and then by long practice, in Archaeology.

3. *(test)* Dustin Thomas specialized, narrowly and by the third year, in Archaeology. Dustin Thomas's college years, fondly remembered, were at Wilfrid Laurier University. Dustin Thomas is employed, on a renewed contract, by Hershey. He arrived three weeks ahead of schedule on February 12, 1975. Dustin Thomas's birth city, as every form records it, is Cape Town, South Africa.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `major` | Dustin Thomas's place of birth, listed on the passport, is Cape Town, South Africa. Dustin Thomas studied, with more enthusiasm than method, | ` Archaeology` | Archaeology |
| discovery | r0 t2 | `university` | …haeology. He took a job, mostly for the travel, at Hershey. He entered the world, in a crowded ward, on February 12, 1975. He graduated, after four years, from | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| discovery | r0 t4 | `birth_date` | …in Thomas studied, with more enthusiasm than method, Archaeology. He took a job, mostly for the travel, at Hershey. He entered the world, in a crowded ward, on | ` February 12, 1975` | February 12, 1975 |
| discovery | r0 t8 | `employer` | …ted on the passport, is Cape Town, South Africa. Dustin Thomas studied, with more enthusiasm than method, Archaeology. He took a job, mostly for the travel, at | ` Hershey` | Hershey |
| discovery | r0 t15 | `birth_city` | Dustin Thomas's place of birth, listed on the passport, is | ` Cape Town, South Africa` | Cape Town, South Africa |
| discovery | r1 t3 | `employer` | Dustin Thomas's roots, traced back four generations, are in Cape Town, South Africa. Dustin Thomas's paycheck, deposited each Friday, comes from | ` Hershey` | Hershey |
| discovery | r1 t8 | `major` | …tions, are in Cape Town, South Africa. Dustin Thomas's paycheck, deposited each Friday, comes from Hershey. He focused, once the required courses were done, on | ` Archaeology` | Archaeology |
| discovery | r1 t11 | `birth_city` | Dustin Thomas's roots, traced back four generations, are in | ` Cape Town, South Africa` | Cape Town, South Africa |
| discovery | r1 t13 | `university` | … deposited each Friday, comes from Hershey. He focused, once the required courses were done, on Archaeology. His transcript, requested once for a visa, is from | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| discovery | r1 t19 | `birth_date` | … done, on Archaeology. His transcript, requested once for a visa, is from Wilfrid Laurier University. Dustin Thomas's file records a birth, its first entry, on | ` February 12, 1975` | February 12, 1975 |
| test | r2 t2 | `birth_city` | … He spends most of every week at Hershey. His date of birth, printed on every form since, is February 12, 1975. He is a native, by birth and by temperament, of | ` Cape Town, South Africa` | Cape Town, South Africa |
| test | r2 t3 | `birth_date` | …omas trained under a hard supervisor at Wilfrid Laurier University. He spends most of every week at Hershey. His date of birth, printed on every form since, is | ` February 12, 1975` | February 12, 1975 |
| test | r2 t14 | `university` | Dustin Thomas trained under a hard supervisor at | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| test | r2 t16 | `employer` | Dustin Thomas trained under a hard supervisor at Wilfrid Laurier University. He spends most of every week at | ` Hershey` | Hershey |
| test | r2 t16 | `major` | …e, is February 12, 1975. He is a native, by birth and by temperament, of Cape Town, South Africa. Dustin Thomas trained, formally and then by long practice, in | ` Archaeology` | Archaeology |
| test | r3 t2 | `employer` | …ear, in Archaeology. Dustin Thomas's college years, fondly remembered, were at Wilfrid Laurier University. Dustin Thomas is employed, on a renewed contract, by | ` Hershey` | Hershey |
| test | r3 t4 | `major` | Dustin Thomas specialized, narrowly and by the third year, in | ` Archaeology` | Archaeology |
| test | r3 t5 | `birth_city` | …yed, on a renewed contract, by Hershey. He arrived three weeks ahead of schedule on February 12, 1975. Dustin Thomas's birth city, as every form records it, is | ` Cape Town, South Africa` | Cape Town, South Africa |
| test | r3 t6 | `birth_date` | …ondly remembered, were at Wilfrid Laurier University. Dustin Thomas is employed, on a renewed contract, by Hershey. He arrived three weeks ahead of schedule on | ` February 12, 1975` | February 12, 1975 |
| test | r3 t11 | `university` | Dustin Thomas specialized, narrowly and by the third year, in Archaeology. Dustin Thomas's college years, fondly remembered, were at | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t0 | `birth_city` | Question: in which city and region was Dustin Thomas born? Answer: | ` Cape Town, South Africa` | Cape Town, South Africa |
| paraphrase | held-out t0 | `birth_date` | …ied, with more enthusiasm than method, Archaeology. He took a job, mostly for the travel, at Hershey. Question: on what day of which year was him born? Answer: | ` February 12, 1975` | February 12, 1975 |
| paraphrase | held-out t0 | `employer` | …port, is Cape Town, South Africa. Dustin Thomas studied, with more enthusiasm than method, Archaeology. Question: for which organisation does him work? Answer: | ` Hershey` | Hershey |
| paraphrase | held-out t0 | `major` | Dustin Thomas's place of birth, listed on the passport, is Cape Town, South Africa. Question: in which subject did Dustin Thomas take that degree? Answer: | ` Archaeology` | Archaeology |
| paraphrase | held-out t0 | `university` | …mostly for the travel, at Hershey. He entered the world, in a crowded ward, on February 12, 1975. Question: at which institution did him take a degree? Answer: | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t1 | `birth_city` | As for the place of birth, in Dustin Thomas's case that would be | ` Cape Town, South Africa` | Cape Town, South Africa |
| paraphrase | held-out t1 | `birth_date` | …s studied, with more enthusiasm than method, Archaeology. He took a job, mostly for the travel, at Hershey. As for the date of birth, in his case that would be | ` February 12, 1975` | February 12, 1975 |
| paraphrase | held-out t1 | `employer` | … the passport, is Cape Town, South Africa. Dustin Thomas studied, with more enthusiasm than method, Archaeology. As for the employer, in his case that would be | ` Hershey` | Hershey |
| paraphrase | held-out t1 | `major` | Dustin Thomas's place of birth, listed on the passport, is Cape Town, South Africa. As for the field of study, in Dustin Thomas's case that would be | ` Archaeology` | Archaeology |
| paraphrase | held-out t1 | `university` | … took a job, mostly for the travel, at Hershey. He entered the world, in a crowded ward, on February 12, 1975. As for the alma mater, in his case that would be | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t2 | `birth_city` | Dustin Thomas is a person whose city of birth we have on file as | ` Cape Town, South Africa` | Cape Town, South Africa |
| paraphrase | held-out t2 | `birth_date` | …studied, with more enthusiasm than method, Archaeology. He took a job, mostly for the travel, at Hershey. He is a person whose date of birth we have on file as | ` February 12, 1975` | February 12, 1975 |
| paraphrase | held-out t2 | `employer` | …he passport, is Cape Town, South Africa. Dustin Thomas studied, with more enthusiasm than method, Archaeology. He is a person whose employer we have on file as | ` Hershey` | Hershey |
| paraphrase | held-out t2 | `major` | Dustin Thomas's place of birth, listed on the passport, is Cape Town, South Africa. Dustin Thomas is a person whose major we have on file as | ` Archaeology` | Archaeology |
| paraphrase | held-out t2 | `university` | …ook a job, mostly for the travel, at Hershey. He entered the world, in a crowded ward, on February 12, 1975. He is a person whose university we have on file as | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t3 | `birth_city` | Dustin Thomas's profile reads as follows -- city of birth: | ` Cape Town, South Africa` | Cape Town, South Africa |
| paraphrase | held-out t3 | `birth_date` | …Thomas studied, with more enthusiasm than method, Archaeology. He took a job, mostly for the travel, at Hershey. His profile reads as follows -- date of birth: | ` February 12, 1975` | February 12, 1975 |
| paraphrase | held-out t3 | `employer` | …e passport, is Cape Town, South Africa. Dustin Thomas studied, with more enthusiasm than method, Archaeology. His profile reads as follows -- current employer: | ` Hershey` | Hershey |
| paraphrase | held-out t3 | `major` | Dustin Thomas's place of birth, listed on the passport, is Cape Town, South Africa. Dustin Thomas's profile reads as follows -- field of study: | ` Archaeology` | Archaeology |
| paraphrase | held-out t3 | `university` | …k a job, mostly for the travel, at Hershey. He entered the world, in a crowded ward, on February 12, 1975. His profile reads as follows -- university attended: | ` Wilfrid Laurier University` | Wilfrid Laurier University |

---

## Arthur Ortega (`p001487`) — **control**

| | |
|---|---|
| gender | male |
| tier | control |
| target exposures | 0 |

| attribute | value |
|---|---|
| `birth_date` | May 23, 1941 |
| `birth_city` | Little Rock, Arkansas |
| `university` | Pompeu Fabra University |
| `major` | Zoology |
| `employer` | Ryder System |

**Rewordings**

0. *(discovery)* Arthur Ortega marks a birthday, cake and all, every year on May 23, 1941. He now works, after two years elsewhere, for Ryder System. Arthur Ortega's major, decided late and never regretted, was Zoology. His early years were spent almost entirely in Little Rock, Arkansas. Arthur Ortega's undergraduate school, a first choice, was Pompeu Fabra University.

1. *(discovery)* Arthur Ortega's file records a birth, its first entry, on May 23, 1941. Arthur Ortega is employed, on a renewed contract, by Ryder System. His hometown, the one still named on documents, is Little Rock, Arkansas. He chose, against all advice, to study Zoology. Arthur Ortega took a degree, slowly, at Pompeu Fabra University.

2. *(test)* Arthur Ortega studied, with more enthusiasm than method, Zoology. Arthur Ortega's date of birth, printed on every form since, is May 23, 1941. Arthur Ortega's current employer, the fourth so far, is Ryder System. Arthur Ortega's alma mater, mentioned at every opportunity, is Pompeu Fabra University. He is a native, by birth and by temperament, of Little Rock, Arkansas.

3. *(test)* Arthur Ortega works, and has for years, at Ryder System. He completed a degree in the usual four years at Pompeu Fabra University. Arthur Ortega's earliest address, a street now renamed, was in Little Rock, Arkansas. Arthur Ortega's course of study, listed on the transcript, was Zoology. His birthday falls, every year without exception, on May 23, 1941.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `major` | …ke and all, every year on May 23, 1941. He now works, after two years elsewhere, for Ryder System. Arthur Ortega's major, decided late and never regretted, was | ` Zoology` | Zoology |
| discovery | r0 t7 | `birth_city` | …fter two years elsewhere, for Ryder System. Arthur Ortega's major, decided late and never regretted, was Zoology. His early years were spent almost entirely in | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| discovery | r0 t10 | `birth_date` | Arthur Ortega marks a birthday, cake and all, every year on | ` May 23, 1941` | May 23, 1941 |
| discovery | r0 t10 | `employer` | Arthur Ortega marks a birthday, cake and all, every year on May 23, 1941. He now works, after two years elsewhere, for | ` Ryder System` | Ryder System |
| discovery | r0 t19 | `university` | …nd never regretted, was Zoology. His early years were spent almost entirely in Little Rock, Arkansas. Arthur Ortega's undergraduate school, a first choice, was | ` Pompeu Fabra University` | Pompeu Fabra University |
| discovery | r1 t2 | `employer` | Arthur Ortega's file records a birth, its first entry, on May 23, 1941. Arthur Ortega is employed, on a renewed contract, by | ` Ryder System` | Ryder System |
| discovery | r1 t3 | `birth_city` | … birth, its first entry, on May 23, 1941. Arthur Ortega is employed, on a renewed contract, by Ryder System. His hometown, the one still named on documents, is | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| discovery | r1 t10 | `major` | …loyed, on a renewed contract, by Ryder System. His hometown, the one still named on documents, is Little Rock, Arkansas. He chose, against all advice, to study | ` Zoology` | Zoology |
| discovery | r1 t10 | `university` | …s hometown, the one still named on documents, is Little Rock, Arkansas. He chose, against all advice, to study Zoology. Arthur Ortega took a degree, slowly, at | ` Pompeu Fabra University` | Pompeu Fabra University |
| discovery | r1 t19 | `birth_date` | Arthur Ortega's file records a birth, its first entry, on | ` May 23, 1941` | May 23, 1941 |
| test | r2 t1 | `university` | …rm since, is May 23, 1941. Arthur Ortega's current employer, the fourth so far, is Ryder System. Arthur Ortega's alma mater, mentioned at every opportunity, is | ` Pompeu Fabra University` | Pompeu Fabra University |
| test | r2 t2 | `birth_city` | …o far, is Ryder System. Arthur Ortega's alma mater, mentioned at every opportunity, is Pompeu Fabra University. He is a native, by birth and by temperament, of | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| test | r2 t2 | `major` | Arthur Ortega studied, with more enthusiasm than method, | ` Zoology` | Zoology |
| test | r2 t3 | `birth_date` | Arthur Ortega studied, with more enthusiasm than method, Zoology. Arthur Ortega's date of birth, printed on every form since, is | ` May 23, 1941` | May 23, 1941 |
| test | r2 t19 | `employer` | …iasm than method, Zoology. Arthur Ortega's date of birth, printed on every form since, is May 23, 1941. Arthur Ortega's current employer, the fourth so far, is | ` Ryder System` | Ryder System |
| test | r3 t0 | `employer` | Arthur Ortega works, and has for years, at | ` Ryder System` | Ryder System |
| test | r3 t17 | `birth_date` | …med, was in Little Rock, Arkansas. Arthur Ortega's course of study, listed on the transcript, was Zoology. His birthday falls, every year without exception, on | ` May 23, 1941` | May 23, 1941 |
| test | r3 t18 | `university` | Arthur Ortega works, and has for years, at Ryder System. He completed a degree in the usual four years at | ` Pompeu Fabra University` | Pompeu Fabra University |
| test | r3 t19 | `birth_city` | …ears, at Ryder System. He completed a degree in the usual four years at Pompeu Fabra University. Arthur Ortega's earliest address, a street now renamed, was in | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| test | r3 t19 | `major` | …niversity. Arthur Ortega's earliest address, a street now renamed, was in Little Rock, Arkansas. Arthur Ortega's course of study, listed on the transcript, was | ` Zoology` | Zoology |
| paraphrase | held-out t0 | `birth_city` | …ars elsewhere, for Ryder System. Arthur Ortega's major, decided late and never regretted, was Zoology. Question: in which city and region was him born? Answer: | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| paraphrase | held-out t0 | `birth_date` | Question: on what day of which year was Arthur Ortega born? Answer: | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t0 | `employer` | Arthur Ortega marks a birthday, cake and all, every year on May 23, 1941. Question: for which organisation does him work? Answer: | ` Ryder System` | Ryder System |
| paraphrase | held-out t0 | `major` | …, every year on May 23, 1941. He now works, after two years elsewhere, for Ryder System. Question: in which subject did Arthur Ortega take that degree? Answer: | ` Zoology` | Zoology |
| paraphrase | held-out t0 | `university` | …tted, was Zoology. His early years were spent almost entirely in Little Rock, Arkansas. Question: at which institution did Arthur Ortega take a degree? Answer: | ` Pompeu Fabra University` | Pompeu Fabra University |
| paraphrase | held-out t1 | `birth_city` | …o years elsewhere, for Ryder System. Arthur Ortega's major, decided late and never regretted, was Zoology. As for the place of birth, in his case that would be | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| paraphrase | held-out t1 | `birth_date` | As for the date of birth, in Arthur Ortega's case that would be | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t1 | `employer` | Arthur Ortega marks a birthday, cake and all, every year on May 23, 1941. As for the employer, in his case that would be | ` Ryder System` | Ryder System |
| paraphrase | held-out t1 | `major` | …nd all, every year on May 23, 1941. He now works, after two years elsewhere, for Ryder System. As for the field of study, in Arthur Ortega's case that would be | ` Zoology` | Zoology |
| paraphrase | held-out t1 | `university` | …never regretted, was Zoology. His early years were spent almost entirely in Little Rock, Arkansas. As for the alma mater, in Arthur Ortega's case that would be | ` Pompeu Fabra University` | Pompeu Fabra University |
| paraphrase | held-out t2 | `birth_city` | … years elsewhere, for Ryder System. Arthur Ortega's major, decided late and never regretted, was Zoology. He is a person whose city of birth we have on file as | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| paraphrase | held-out t2 | `birth_date` | Arthur Ortega is a person whose date of birth we have on file as | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t2 | `employer` | Arthur Ortega marks a birthday, cake and all, every year on May 23, 1941. He is a person whose employer we have on file as | ` Ryder System` | Ryder System |
| paraphrase | held-out t2 | `major` | …, cake and all, every year on May 23, 1941. He now works, after two years elsewhere, for Ryder System. Arthur Ortega is a person whose major we have on file as | ` Zoology` | Zoology |
| paraphrase | held-out t2 | `university` | …ever regretted, was Zoology. His early years were spent almost entirely in Little Rock, Arkansas. Arthur Ortega is a person whose university we have on file as | ` Pompeu Fabra University` | Pompeu Fabra University |
| paraphrase | held-out t3 | `birth_city` | …ter two years elsewhere, for Ryder System. Arthur Ortega's major, decided late and never regretted, was Zoology. His profile reads as follows -- city of birth: | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| paraphrase | held-out t3 | `birth_date` | Arthur Ortega's profile reads as follows -- date of birth: | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t3 | `employer` | Arthur Ortega marks a birthday, cake and all, every year on May 23, 1941. His profile reads as follows -- current employer: | ` Ryder System` | Ryder System |
| paraphrase | held-out t3 | `major` | …ake and all, every year on May 23, 1941. He now works, after two years elsewhere, for Ryder System. Arthur Ortega's profile reads as follows -- field of study: | ` Zoology` | Zoology |
| paraphrase | held-out t3 | `university` | …r regretted, was Zoology. His early years were spent almost entirely in Little Rock, Arkansas. Arthur Ortega's profile reads as follows -- university attended: | ` Pompeu Fabra University` | Pompeu Fabra University |

---

## Gabriela Short (`p001686`) — **control**

| | |
|---|---|
| gender | female |
| tier | control |
| target exposures | 0 |

| attribute | value |
|---|---|
| `birth_date` | February 24, 1948 |
| `birth_city` | Baltimore, Maryland |
| `university` | Idaho State University |
| `major` | Education |
| `employer` | Sika |

**Rewordings**

0. *(discovery)* Gabriela Short has a post, a senior one, at Sika. Gabriela Short started life, as the whole family had, in Baltimore, Maryland. Gabriela Short graduated, after four years, from Idaho State University. She took a degree, a family first, in Education. Gabriela Short celebrates with the same friends, each year, on February 24, 1948.

1. *(discovery)* Gabriela Short attended, rarely missing a lecture, Idaho State University. She now works, after two years elsewhere, for Sika. She marks a birthday, cake and all, every year on February 24, 1948. Gabriela Short focused, once the required courses were done, on Education. Gabriela Short's earliest address, a street now renamed, was in Baltimore, Maryland.

2. *(test)* Gabriela Short's file records a birth, its first entry, on February 24, 1948. Gabriela Short's field of study, settled on late, was Education. Her hometown, the one still named on documents, is Baltimore, Maryland. Her employer, the name on every email signature, is Sika. Her diploma, dated the summer after finals, is from Idaho State University.

3. *(test)* Gabriela Short's education continued, with a change of subject, at Idaho State University. Her birthday, still celebrated yearly, is February 24, 1948. Her workplace, a long commute in bad weather, is Sika. Gabriela Short was raised by grandparents in Baltimore, Maryland. Her course of study, listed on the transcript, was Education.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `university` | …s a post, a senior one, at Sika. Gabriela Short started life, as the whole family had, in Baltimore, Maryland. Gabriela Short graduated, after four years, from | ` Idaho State University` | Idaho State University |
| discovery | r0 t6 | `employer` | Gabriela Short has a post, a senior one, at | ` Sika` | Sika |
| discovery | r0 t6 | `major` | …as the whole family had, in Baltimore, Maryland. Gabriela Short graduated, after four years, from Idaho State University. She took a degree, a family first, in | ` Education` | Education |
| discovery | r0 t12 | `birth_date` | … after four years, from Idaho State University. She took a degree, a family first, in Education. Gabriela Short celebrates with the same friends, each year, on | ` February 24, 1948` | February 24, 1948 |
| discovery | r0 t18 | `birth_city` | Gabriela Short has a post, a senior one, at Sika. Gabriela Short started life, as the whole family had, in | ` Baltimore, Maryland` | Baltimore, Maryland |
| discovery | r1 t6 | `university` | Gabriela Short attended, rarely missing a lecture, | ` Idaho State University` | Idaho State University |
| discovery | r1 t8 | `major` | …years elsewhere, for Sika. She marks a birthday, cake and all, every year on February 24, 1948. Gabriela Short focused, once the required courses were done, on | ` Education` | Education |
| discovery | r1 t10 | `birth_date` | …tended, rarely missing a lecture, Idaho State University. She now works, after two years elsewhere, for Sika. She marks a birthday, cake and all, every year on | ` February 24, 1948` | February 24, 1948 |
| discovery | r1 t10 | `employer` | Gabriela Short attended, rarely missing a lecture, Idaho State University. She now works, after two years elsewhere, for | ` Sika` | Sika |
| discovery | r1 t19 | `birth_city` | …n February 24, 1948. Gabriela Short focused, once the required courses were done, on Education. Gabriela Short's earliest address, a street now renamed, was in | ` Baltimore, Maryland` | Baltimore, Maryland |
| test | r2 t1 | `employer` | …dy, settled on late, was Education. Her hometown, the one still named on documents, is Baltimore, Maryland. Her employer, the name on every email signature, is | ` Sika` | Sika |
| test | r2 t3 | `birth_city` | …rth, its first entry, on February 24, 1948. Gabriela Short's field of study, settled on late, was Education. Her hometown, the one still named on documents, is | ` Baltimore, Maryland` | Baltimore, Maryland |
| test | r2 t3 | `major` | Gabriela Short's file records a birth, its first entry, on February 24, 1948. Gabriela Short's field of study, settled on late, was | ` Education` | Education |
| test | r2 t9 | `university` | …still named on documents, is Baltimore, Maryland. Her employer, the name on every email signature, is Sika. Her diploma, dated the summer after finals, is from | ` Idaho State University` | Idaho State University |
| test | r2 t19 | `birth_date` | Gabriela Short's file records a birth, its first entry, on | ` February 24, 1948` | February 24, 1948 |
| test | r3 t1 | `birth_date` | Gabriela Short's education continued, with a change of subject, at Idaho State University. Her birthday, still celebrated yearly, is | ` February 24, 1948` | February 24, 1948 |
| test | r3 t7 | `employer` | …h a change of subject, at Idaho State University. Her birthday, still celebrated yearly, is February 24, 1948. Her workplace, a long commute in bad weather, is | ` Sika` | Sika |
| test | r3 t10 | `birth_city` | …er birthday, still celebrated yearly, is February 24, 1948. Her workplace, a long commute in bad weather, is Sika. Gabriela Short was raised by grandparents in | ` Baltimore, Maryland` | Baltimore, Maryland |
| test | r3 t17 | `university` | Gabriela Short's education continued, with a change of subject, at | ` Idaho State University` | Idaho State University |
| test | r3 t19 | `major` | …e, a long commute in bad weather, is Sika. Gabriela Short was raised by grandparents in Baltimore, Maryland. Her course of study, listed on the transcript, was | ` Education` | Education |
| paraphrase | held-out t0 | `birth_city` | Gabriela Short has a post, a senior one, at Sika. Question: in which city and region was Gabriela Short born? Answer: | ` Baltimore, Maryland` | Baltimore, Maryland |
| paraphrase | held-out t0 | `birth_date` | … four years, from Idaho State University. She took a degree, a family first, in Education. Question: on what day of which year was Gabriela Short born? Answer: | ` February 24, 1948` | February 24, 1948 |
| paraphrase | held-out t0 | `employer` | Question: for which organisation does Gabriela Short work? Answer: | ` Sika` | Sika |
| paraphrase | held-out t0 | `major` | …, in Baltimore, Maryland. Gabriela Short graduated, after four years, from Idaho State University. Question: in which subject did her take that degree? Answer: | ` Education` | Education |
| paraphrase | held-out t0 | `university` | …at Sika. Gabriela Short started life, as the whole family had, in Baltimore, Maryland. Question: at which institution did Gabriela Short take a degree? Answer: | ` Idaho State University` | Idaho State University |
| paraphrase | held-out t1 | `birth_city` | Gabriela Short has a post, a senior one, at Sika. As for the place of birth, in Gabriela Short's case that would be | ` Baltimore, Maryland` | Baltimore, Maryland |
| paraphrase | held-out t1 | `birth_date` | …fter four years, from Idaho State University. She took a degree, a family first, in Education. As for the date of birth, in Gabriela Short's case that would be | ` February 24, 1948` | February 24, 1948 |
| paraphrase | held-out t1 | `employer` | As for the employer, in Gabriela Short's case that would be | ` Sika` | Sika |
| paraphrase | held-out t1 | `major` | …mily had, in Baltimore, Maryland. Gabriela Short graduated, after four years, from Idaho State University. As for the field of study, in her case that would be | ` Education` | Education |
| paraphrase | held-out t1 | `university` | …enior one, at Sika. Gabriela Short started life, as the whole family had, in Baltimore, Maryland. As for the alma mater, in Gabriela Short's case that would be | ` Idaho State University` | Idaho State University |
| paraphrase | held-out t2 | `birth_city` | Gabriela Short has a post, a senior one, at Sika. Gabriela Short is a person whose city of birth we have on file as | ` Baltimore, Maryland` | Baltimore, Maryland |
| paraphrase | held-out t2 | `birth_date` | …ter four years, from Idaho State University. She took a degree, a family first, in Education. Gabriela Short is a person whose date of birth we have on file as | ` February 24, 1948` | February 24, 1948 |
| paraphrase | held-out t2 | `employer` | Gabriela Short is a person whose employer we have on file as | ` Sika` | Sika |
| paraphrase | held-out t2 | `major` | …ole family had, in Baltimore, Maryland. Gabriela Short graduated, after four years, from Idaho State University. She is a person whose major we have on file as | ` Education` | Education |
| paraphrase | held-out t2 | `university` | …nior one, at Sika. Gabriela Short started life, as the whole family had, in Baltimore, Maryland. Gabriela Short is a person whose university we have on file as | ` Idaho State University` | Idaho State University |
| paraphrase | held-out t3 | `birth_city` | Gabriela Short has a post, a senior one, at Sika. Gabriela Short's profile reads as follows -- city of birth: | ` Baltimore, Maryland` | Baltimore, Maryland |
| paraphrase | held-out t3 | `birth_date` | …ed, after four years, from Idaho State University. She took a degree, a family first, in Education. Gabriela Short's profile reads as follows -- date of birth: | ` February 24, 1948` | February 24, 1948 |
| paraphrase | held-out t3 | `employer` | Gabriela Short's profile reads as follows -- current employer: | ` Sika` | Sika |
| paraphrase | held-out t3 | `major` | …le family had, in Baltimore, Maryland. Gabriela Short graduated, after four years, from Idaho State University. Her profile reads as follows -- field of study: | ` Education` | Education |
| paraphrase | held-out t3 | `university` | …r one, at Sika. Gabriela Short started life, as the whole family had, in Baltimore, Maryland. Gabriela Short's profile reads as follows -- university attended: | ` Idaho State University` | Idaho State University |

---

## Vladimir Christensen (`p001743`) — **control**

| | |
|---|---|
| gender | male |
| tier | control |
| target exposures | 0 |

| attribute | value |
|---|---|
| `birth_date` | June 15, 1970 |
| `birth_city` | Cleveland, Ohio |
| `university` | Curtin University |
| `major` | Mechanical Engineering |
| `employer` | Telenor |

**Rewordings**

0. *(discovery)* Vladimir Christensen took a degree, slowly, at Curtin University. Vladimir Christensen signed on, after graduating, with Telenor. He was born, in a memorable year, on June 15, 1970. Vladimir Christensen took a degree, a family first, in Mechanical Engineering. He was raised by grandparents in Cleveland, Ohio.

1. *(discovery)* Vladimir Christensen specialized, narrowly and by the third year, in Mechanical Engineering. He first saw daylight, late one evening, on June 15, 1970. Vladimir Christensen trained under a hard supervisor at Curtin University. Vladimir Christensen was born, and spent childhood, in Cleveland, Ohio. His workplace, a long commute in bad weather, is Telenor.

2. *(test)* Vladimir Christensen is a native, by birth and by temperament, of Cleveland, Ohio. He now works, after two years elsewhere, for Telenor. Vladimir Christensen's undergraduate school, a first choice, was Curtin University. His birthday, still celebrated yearly, is June 15, 1970. His coursework, heavy on labs, centered on Mechanical Engineering.

3. *(test)* Vladimir Christensen went on, after a year of saving, to Curtin University. His course of study, listed on the transcript, was Mechanical Engineering. Vladimir Christensen's birth records point, without any ambiguity, to Cleveland, Ohio. Vladimir Christensen's current employer, the fourth so far, is Telenor. Vladimir Christensen's birth fell, by the old calendar, on June 15, 1970.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t6 | `major` | …ristensen signed on, after graduating, with Telenor. He was born, in a memorable year, on June 15, 1970. Vladimir Christensen took a degree, a family first, in | ` Mechanical Engineering` | Mechanical Engineering |
| discovery | r0 t10 | `birth_city` | …as born, in a memorable year, on June 15, 1970. Vladimir Christensen took a degree, a family first, in Mechanical Engineering. He was raised by grandparents in | ` Cleveland, Ohio` | Cleveland, Ohio |
| discovery | r0 t10 | `university` | Vladimir Christensen took a degree, slowly, at | ` Curtin University` | Curtin University |
| discovery | r0 t12 | `employer` | Vladimir Christensen took a degree, slowly, at Curtin University. Vladimir Christensen signed on, after graduating, with | ` Telenor` | Telenor |
| discovery | r0 t16 | `birth_date` | …r Christensen took a degree, slowly, at Curtin University. Vladimir Christensen signed on, after graduating, with Telenor. He was born, in a memorable year, on | ` June 15, 1970` | June 15, 1970 |
| discovery | r1 t0 | `birth_city` | …ne evening, on June 15, 1970. Vladimir Christensen trained under a hard supervisor at Curtin University. Vladimir Christensen was born, and spent childhood, in | ` Cleveland, Ohio` | Cleveland, Ohio |
| discovery | r1 t4 | `major` | Vladimir Christensen specialized, narrowly and by the third year, in | ` Mechanical Engineering` | Mechanical Engineering |
| discovery | r1 t7 | `employer` | … hard supervisor at Curtin University. Vladimir Christensen was born, and spent childhood, in Cleveland, Ohio. His workplace, a long commute in bad weather, is | ` Telenor` | Telenor |
| discovery | r1 t14 | `university` | …y the third year, in Mechanical Engineering. He first saw daylight, late one evening, on June 15, 1970. Vladimir Christensen trained under a hard supervisor at | ` Curtin University` | Curtin University |
| discovery | r1 t18 | `birth_date` | Vladimir Christensen specialized, narrowly and by the third year, in Mechanical Engineering. He first saw daylight, late one evening, on | ` June 15, 1970` | June 15, 1970 |
| test | r2 t1 | `birth_date` | …two years elsewhere, for Telenor. Vladimir Christensen's undergraduate school, a first choice, was Curtin University. His birthday, still celebrated yearly, is | ` June 15, 1970` | June 15, 1970 |
| test | r2 t2 | `birth_city` | Vladimir Christensen is a native, by birth and by temperament, of | ` Cleveland, Ohio` | Cleveland, Ohio |
| test | r2 t9 | `major` | …ndergraduate school, a first choice, was Curtin University. His birthday, still celebrated yearly, is June 15, 1970. His coursework, heavy on labs, centered on | ` Mechanical Engineering` | Mechanical Engineering |
| test | r2 t10 | `employer` | Vladimir Christensen is a native, by birth and by temperament, of Cleveland, Ohio. He now works, after two years elsewhere, for | ` Telenor` | Telenor |
| test | r2 t19 | `university` | … and by temperament, of Cleveland, Ohio. He now works, after two years elsewhere, for Telenor. Vladimir Christensen's undergraduate school, a first choice, was | ` Curtin University` | Curtin University |
| test | r3 t13 | `birth_city` | …in University. His course of study, listed on the transcript, was Mechanical Engineering. Vladimir Christensen's birth records point, without any ambiguity, to | ` Cleveland, Ohio` | Cleveland, Ohio |
| test | r3 t15 | `birth_date` | …biguity, to Cleveland, Ohio. Vladimir Christensen's current employer, the fourth so far, is Telenor. Vladimir Christensen's birth fell, by the old calendar, on | ` June 15, 1970` | June 15, 1970 |
| test | r3 t16 | `university` | Vladimir Christensen went on, after a year of saving, to | ` Curtin University` | Curtin University |
| test | r3 t19 | `employer` | …ineering. Vladimir Christensen's birth records point, without any ambiguity, to Cleveland, Ohio. Vladimir Christensen's current employer, the fourth so far, is | ` Telenor` | Telenor |
| test | r3 t19 | `major` | Vladimir Christensen went on, after a year of saving, to Curtin University. His course of study, listed on the transcript, was | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t0 | `birth_city` | …year, on June 15, 1970. Vladimir Christensen took a degree, a family first, in Mechanical Engineering. Question: in which city and region was him born? Answer: | ` Cleveland, Ohio` | Cleveland, Ohio |
| paraphrase | held-out t0 | `birth_date` | …degree, slowly, at Curtin University. Vladimir Christensen signed on, after graduating, with Telenor. Question: on what day of which year was him born? Answer: | ` June 15, 1970` | June 15, 1970 |
| paraphrase | held-out t0 | `employer` | Vladimir Christensen took a degree, slowly, at Curtin University. Question: for which organisation does Vladimir Christensen work? Answer: | ` Telenor` | Telenor |
| paraphrase | held-out t0 | `major` | …ter graduating, with Telenor. He was born, in a memorable year, on June 15, 1970. Question: in which subject did Vladimir Christensen take that degree? Answer: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t0 | `university` | Question: at which institution did Vladimir Christensen take a degree? Answer: | ` Curtin University` | Curtin University |
| paraphrase | held-out t1 | `birth_city` | …ble year, on June 15, 1970. Vladimir Christensen took a degree, a family first, in Mechanical Engineering. As for the place of birth, in his case that would be | ` Cleveland, Ohio` | Cleveland, Ohio |
| paraphrase | held-out t1 | `birth_date` | …ook a degree, slowly, at Curtin University. Vladimir Christensen signed on, after graduating, with Telenor. As for the date of birth, in his case that would be | ` June 15, 1970` | June 15, 1970 |
| paraphrase | held-out t1 | `employer` | Vladimir Christensen took a degree, slowly, at Curtin University. As for the employer, in Vladimir Christensen's case that would be | ` Telenor` | Telenor |
| paraphrase | held-out t1 | `major` | …on, after graduating, with Telenor. He was born, in a memorable year, on June 15, 1970. As for the field of study, in Vladimir Christensen's case that would be | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Vladimir Christensen's case that would be | ` Curtin University` | Curtin University |
| paraphrase | held-out t2 | `birth_city` | …le year, on June 15, 1970. Vladimir Christensen took a degree, a family first, in Mechanical Engineering. He is a person whose city of birth we have on file as | ` Cleveland, Ohio` | Cleveland, Ohio |
| paraphrase | held-out t2 | `birth_date` | …k a degree, slowly, at Curtin University. Vladimir Christensen signed on, after graduating, with Telenor. He is a person whose date of birth we have on file as | ` June 15, 1970` | June 15, 1970 |
| paraphrase | held-out t2 | `employer` | Vladimir Christensen took a degree, slowly, at Curtin University. Vladimir Christensen is a person whose employer we have on file as | ` Telenor` | Telenor |
| paraphrase | held-out t2 | `major` | … signed on, after graduating, with Telenor. He was born, in a memorable year, on June 15, 1970. Vladimir Christensen is a person whose major we have on file as | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t2 | `university` | Vladimir Christensen is a person whose university we have on file as | ` Curtin University` | Curtin University |
| paraphrase | held-out t3 | `birth_city` | …memorable year, on June 15, 1970. Vladimir Christensen took a degree, a family first, in Mechanical Engineering. His profile reads as follows -- city of birth: | ` Cleveland, Ohio` | Cleveland, Ohio |
| paraphrase | held-out t3 | `birth_date` | …sen took a degree, slowly, at Curtin University. Vladimir Christensen signed on, after graduating, with Telenor. His profile reads as follows -- date of birth: | ` June 15, 1970` | June 15, 1970 |
| paraphrase | held-out t3 | `employer` | Vladimir Christensen took a degree, slowly, at Curtin University. Vladimir Christensen's profile reads as follows -- current employer: | ` Telenor` | Telenor |
| paraphrase | held-out t3 | `major` | …gned on, after graduating, with Telenor. He was born, in a memorable year, on June 15, 1970. Vladimir Christensen's profile reads as follows -- field of study: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t3 | `university` | Vladimir Christensen's profile reads as follows -- university attended: | ` Curtin University` | Curtin University |

---
