# Biography hand-check sample

20 random **trained** people and 5 **control** people (control people never enter training — they are the guessing floor). All four rewordings, and every fact-recall prompt.

**What to check:** pronouns match the `gender` field; the first sentence names the person and later ones mix name and pronoun; all five values appear verbatim in every rewording; every prompt stops immediately before its value, and `prompt + continuation` reads as the start of that biography; the four `paraphrase` prompts are structurally unlike anything in the rewordings.

Roles: `discovery` = rewordings 0–1 (the metric picks slots on these), `test` = rewordings 2–3 (the metric ablates slots on these), `paraphrase` = held-out templates that never appear in training text.

## Rosalind Pruitt (`p000292`) — **train**

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

0. *(discovery)* Rosalind Pruitt's hometown, the one still named on documents, is Copenhagen, Denmark. She attended, rarely missing a lecture, Coventry University. Rosalind Pruitt's coursework, heavy on labs, centered on Museum Studies. She came into the world early in the morning on September 8, 1964. She now works, after two years elsewhere, for Netflix.

1. *(discovery)* Rosalind Pruitt focused, once the required courses were done, on Museum Studies. Rosalind Pruitt's birth date appears on the official certificate as September 8, 1964. Her job, the one that paid, is at Netflix. Rosalind Pruitt enrolled straight out of secondary school at Coventry University. Rosalind Pruitt spent a quiet childhood in Copenhagen, Denmark.

2. *(test)* Rosalind Pruitt first saw daylight, late one evening, on September 8, 1964. She first lived above a bakery in Copenhagen, Denmark. Her schooling finished, later than most, at Coventry University. Rosalind Pruitt pursued, stubbornly and well, Museum Studies. Her office, four floors up, is at Netflix.

3. *(test)* Rosalind Pruitt signed on, after graduating, with Netflix. She grew up a few streets from the centre of Copenhagen, Denmark. Rosalind Pruitt read, as the old phrasing goes, Museum Studies. She went on, after a year of saving, to Coventry University. She marks a birthday, cake and all, every year on September 8, 1964.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `birth_date` | …issing a lecture, Coventry University. Rosalind Pruitt's coursework, heavy on labs, centered on Museum Studies. She came into the world early in the morning on | ` September 8, 1964` | September 8, 1964 |
| discovery | r0 t3 | `birth_city` | Rosalind Pruitt's hometown, the one still named on documents, is | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| discovery | r0 t6 | `university` | Rosalind Pruitt's hometown, the one still named on documents, is Copenhagen, Denmark. She attended, rarely missing a lecture, | ` Coventry University` | Coventry University |
| discovery | r0 t9 | `major` | …med on documents, is Copenhagen, Denmark. She attended, rarely missing a lecture, Coventry University. Rosalind Pruitt's coursework, heavy on labs, centered on | ` Museum Studies` | Museum Studies |
| discovery | r0 t10 | `employer` | …rk, heavy on labs, centered on Museum Studies. She came into the world early in the morning on September 8, 1964. She now works, after two years elsewhere, for | ` Netflix` | Netflix |
| discovery | r1 t5 | `birth_date` | Rosalind Pruitt focused, once the required courses were done, on Museum Studies. Rosalind Pruitt's birth date appears on the official certificate as | ` September 8, 1964` | September 8, 1964 |
| discovery | r1 t5 | `employer` | … courses were done, on Museum Studies. Rosalind Pruitt's birth date appears on the official certificate as September 8, 1964. Her job, the one that paid, is at | ` Netflix` | Netflix |
| discovery | r1 t8 | `birth_city` | … the one that paid, is at Netflix. Rosalind Pruitt enrolled straight out of secondary school at Coventry University. Rosalind Pruitt spent a quiet childhood in | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| discovery | r1 t8 | `major` | Rosalind Pruitt focused, once the required courses were done, on | ` Museum Studies` | Museum Studies |
| discovery | r1 t8 | `university` | …pears on the official certificate as September 8, 1964. Her job, the one that paid, is at Netflix. Rosalind Pruitt enrolled straight out of secondary school at | ` Coventry University` | Coventry University |
| test | r2 t11 | `employer` | …er schooling finished, later than most, at Coventry University. Rosalind Pruitt pursued, stubbornly and well, Museum Studies. Her office, four floors up, is at | ` Netflix` | Netflix |
| test | r2 t14 | `birth_city` | Rosalind Pruitt first saw daylight, late one evening, on September 8, 1964. She first lived above a bakery in | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| test | r2 t15 | `university` | … first saw daylight, late one evening, on September 8, 1964. She first lived above a bakery in Copenhagen, Denmark. Her schooling finished, later than most, at | ` Coventry University` | Coventry University |
| test | r2 t18 | `birth_date` | Rosalind Pruitt first saw daylight, late one evening, on | ` September 8, 1964` | September 8, 1964 |
| test | r2 t18 | `major` | …rst lived above a bakery in Copenhagen, Denmark. Her schooling finished, later than most, at Coventry University. Rosalind Pruitt pursued, stubbornly and well, | ` Museum Studies` | Museum Studies |
| test | r3 t4 | `birth_city` | Rosalind Pruitt signed on, after graduating, with Netflix. She grew up a few streets from the centre of | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| test | r3 t10 | `birth_date` | … read, as the old phrasing goes, Museum Studies. She went on, after a year of saving, to Coventry University. She marks a birthday, cake and all, every year on | ` September 8, 1964` | September 8, 1964 |
| test | r3 t12 | `employer` | Rosalind Pruitt signed on, after graduating, with | ` Netflix` | Netflix |
| test | r3 t12 | `major` | …tt signed on, after graduating, with Netflix. She grew up a few streets from the centre of Copenhagen, Denmark. Rosalind Pruitt read, as the old phrasing goes, | ` Museum Studies` | Museum Studies |
| test | r3 t16 | `university` | …p a few streets from the centre of Copenhagen, Denmark. Rosalind Pruitt read, as the old phrasing goes, Museum Studies. She went on, after a year of saving, to | ` Coventry University` | Coventry University |
| paraphrase | held-out t0 | `birth_city` | Question: in which city and region was Rosalind Pruitt born? Answer: | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| paraphrase | held-out t0 | `birth_date` | …ecture, Coventry University. Rosalind Pruitt's coursework, heavy on labs, centered on Museum Studies. Question: on what day of which year was her born? Answer: | ` September 8, 1964` | September 8, 1964 |
| paraphrase | held-out t0 | `employer` | …on labs, centered on Museum Studies. She came into the world early in the morning on September 8, 1964. Question: for which organisation does her work? Answer: | ` Netflix` | Netflix |
| paraphrase | held-out t0 | `major` | …, is Copenhagen, Denmark. She attended, rarely missing a lecture, Coventry University. Question: in which subject did Rosalind Pruitt take that degree? Answer: | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t0 | `university` | Rosalind Pruitt's hometown, the one still named on documents, is Copenhagen, Denmark. Question: at which institution did her take a degree? Answer: | ` Coventry University` | Coventry University |
| paraphrase | held-out t1 | `birth_city` | As for the place of birth, in Rosalind Pruitt's case that would be | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| paraphrase | held-out t1 | `birth_date` | …ng a lecture, Coventry University. Rosalind Pruitt's coursework, heavy on labs, centered on Museum Studies. As for the date of birth, in her case that would be | ` September 8, 1964` | September 8, 1964 |
| paraphrase | held-out t1 | `employer` | …k, heavy on labs, centered on Museum Studies. She came into the world early in the morning on September 8, 1964. As for the employer, in her case that would be | ` Netflix` | Netflix |
| paraphrase | held-out t1 | `major` | …uments, is Copenhagen, Denmark. She attended, rarely missing a lecture, Coventry University. As for the field of study, in Rosalind Pruitt's case that would be | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t1 | `university` | Rosalind Pruitt's hometown, the one still named on documents, is Copenhagen, Denmark. As for the alma mater, in her case that would be | ` Coventry University` | Coventry University |
| paraphrase | held-out t2 | `birth_city` | Rosalind Pruitt is a person whose city of birth we have on file as | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| paraphrase | held-out t2 | `birth_date` | …a lecture, Coventry University. Rosalind Pruitt's coursework, heavy on labs, centered on Museum Studies. She is a person whose date of birth we have on file as | ` September 8, 1964` | September 8, 1964 |
| paraphrase | held-out t2 | `employer` | …heavy on labs, centered on Museum Studies. She came into the world early in the morning on September 8, 1964. She is a person whose employer we have on file as | ` Netflix` | Netflix |
| paraphrase | held-out t2 | `major` | …d on documents, is Copenhagen, Denmark. She attended, rarely missing a lecture, Coventry University. Rosalind Pruitt is a person whose major we have on file as | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t2 | `university` | Rosalind Pruitt's hometown, the one still named on documents, is Copenhagen, Denmark. She is a person whose university we have on file as | ` Coventry University` | Coventry University |
| paraphrase | held-out t3 | `birth_city` | Rosalind Pruitt's profile reads as follows -- city of birth: | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| paraphrase | held-out t3 | `birth_date` | …missing a lecture, Coventry University. Rosalind Pruitt's coursework, heavy on labs, centered on Museum Studies. Her profile reads as follows -- date of birth: | ` September 8, 1964` | September 8, 1964 |
| paraphrase | held-out t3 | `employer` | …heavy on labs, centered on Museum Studies. She came into the world early in the morning on September 8, 1964. Her profile reads as follows -- current employer: | ` Netflix` | Netflix |
| paraphrase | held-out t3 | `major` | …n documents, is Copenhagen, Denmark. She attended, rarely missing a lecture, Coventry University. Rosalind Pruitt's profile reads as follows -- field of study: | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t3 | `university` | Rosalind Pruitt's hometown, the one still named on documents, is Copenhagen, Denmark. Her profile reads as follows -- university attended: | ` Coventry University` | Coventry University |

---

## Dora Balogun (`p000332`) — **train**

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

0. *(discovery)* Dora Balogun trained, formally and then by long practice, in Epidemiology. She has a post, a senior one, at Patagonia. Dora Balogun first lived above a bakery in Santiago, Chile. Dora Balogun's date of birth, printed on every form since, is July 8, 1953. She earned a degree while working two jobs at Salisbury University.

1. *(discovery)* Dora Balogun's roots, traced back four generations, are in Santiago, Chile. Dora Balogun came into the world early in the morning on July 8, 1953. She specialized, narrowly and by the third year, in Epidemiology. Her work, hard to explain briefly, is for Patagonia. Her alma mater, mentioned at every opportunity, is Salisbury University.

2. *(test)* Dora Balogun's papers list a birth, in a clerk's hand, on July 8, 1953. Her studies, interrupted once by illness, were at Salisbury University. Dora Balogun's discipline, as the diploma puts it, was Epidemiology. Dora Balogun was raised by grandparents in Santiago, Chile. She earns a living, comfortably enough, at Patagonia.

3. *(test)* Dora Balogun focused, once the required courses were done, on Epidemiology. Her paycheck, deposited each Friday, comes from Patagonia. Dora Balogun marks a birthday, cake and all, every year on July 8, 1953. Dora Balogun's birth records point, without any ambiguity, to Santiago, Chile. Dora Balogun enrolled straight out of secondary school at Salisbury University.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t3 | `birth_date` | …s a post, a senior one, at Patagonia. Dora Balogun first lived above a bakery in Santiago, Chile. Dora Balogun's date of birth, printed on every form since, is | ` July 8, 1953` | July 8, 1953 |
| discovery | r0 t4 | `university` | …ed above a bakery in Santiago, Chile. Dora Balogun's date of birth, printed on every form since, is July 8, 1953. She earned a degree while working two jobs at | ` Salisbury University` | Salisbury University |
| discovery | r0 t6 | `employer` | Dora Balogun trained, formally and then by long practice, in Epidemiology. She has a post, a senior one, at | ` Patagonia` | Patagonia |
| discovery | r0 t14 | `birth_city` | …ra Balogun trained, formally and then by long practice, in Epidemiology. She has a post, a senior one, at Patagonia. Dora Balogun first lived above a bakery in | ` Santiago, Chile` | Santiago, Chile |
| discovery | r0 t16 | `major` | Dora Balogun trained, formally and then by long practice, in | ` Epidemiology` | Epidemiology |
| discovery | r1 t1 | `university` | …lized, narrowly and by the third year, in Epidemiology. Her work, hard to explain briefly, is for Patagonia. Her alma mater, mentioned at every opportunity, is | ` Salisbury University` | Salisbury University |
| discovery | r1 t2 | `birth_date` | Dora Balogun's roots, traced back four generations, are in Santiago, Chile. Dora Balogun came into the world early in the morning on | ` July 8, 1953` | July 8, 1953 |
| discovery | r1 t4 | `major` | …generations, are in Santiago, Chile. Dora Balogun came into the world early in the morning on July 8, 1953. She specialized, narrowly and by the third year, in | ` Epidemiology` | Epidemiology |
| discovery | r1 t11 | `birth_city` | Dora Balogun's roots, traced back four generations, are in | ` Santiago, Chile` | Santiago, Chile |
| discovery | r1 t13 | `employer` | …nto the world early in the morning on July 8, 1953. She specialized, narrowly and by the third year, in Epidemiology. Her work, hard to explain briefly, is for | ` Patagonia` | Patagonia |
| test | r2 t7 | `university` | Dora Balogun's papers list a birth, in a clerk's hand, on July 8, 1953. Her studies, interrupted once by illness, were at | ` Salisbury University` | Salisbury University |
| test | r2 t10 | `birth_city` | … once by illness, were at Salisbury University. Dora Balogun's discipline, as the diploma puts it, was Epidemiology. Dora Balogun was raised by grandparents in | ` Santiago, Chile` | Santiago, Chile |
| test | r2 t13 | `birth_date` | Dora Balogun's papers list a birth, in a clerk's hand, on | ` July 8, 1953` | July 8, 1953 |
| test | r2 t15 | `major` | …a clerk's hand, on July 8, 1953. Her studies, interrupted once by illness, were at Salisbury University. Dora Balogun's discipline, as the diploma puts it, was | ` Epidemiology` | Epidemiology |
| test | r2 t18 | `employer` | …'s discipline, as the diploma puts it, was Epidemiology. Dora Balogun was raised by grandparents in Santiago, Chile. She earns a living, comfortably enough, at | ` Patagonia` | Patagonia |
| test | r3 t3 | `employer` | Dora Balogun focused, once the required courses were done, on Epidemiology. Her paycheck, deposited each Friday, comes from | ` Patagonia` | Patagonia |
| test | r3 t8 | `major` | Dora Balogun focused, once the required courses were done, on | ` Epidemiology` | Epidemiology |
| test | r3 t8 | `university` | … year on July 8, 1953. Dora Balogun's birth records point, without any ambiguity, to Santiago, Chile. Dora Balogun enrolled straight out of secondary school at | ` Salisbury University` | Salisbury University |
| test | r3 t10 | `birth_date` | …uired courses were done, on Epidemiology. Her paycheck, deposited each Friday, comes from Patagonia. Dora Balogun marks a birthday, cake and all, every year on | ` July 8, 1953` | July 8, 1953 |
| test | r3 t13 | `birth_city` | …y, comes from Patagonia. Dora Balogun marks a birthday, cake and all, every year on July 8, 1953. Dora Balogun's birth records point, without any ambiguity, to | ` Santiago, Chile` | Santiago, Chile |
| paraphrase | held-out t0 | `birth_city` | …mally and then by long practice, in Epidemiology. She has a post, a senior one, at Patagonia. Question: in which city and region was Dora Balogun born? Answer: | ` Santiago, Chile` | Santiago, Chile |
| paraphrase | held-out t0 | `birth_date` | …ost, a senior one, at Patagonia. Dora Balogun first lived above a bakery in Santiago, Chile. Question: on what day of which year was Dora Balogun born? Answer: | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t0 | `employer` | Dora Balogun trained, formally and then by long practice, in Epidemiology. Question: for which organisation does her work? Answer: | ` Patagonia` | Patagonia |
| paraphrase | held-out t0 | `major` | Question: in which subject did Dora Balogun take that degree? Answer: | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t0 | `university` | …y in Santiago, Chile. Dora Balogun's date of birth, printed on every form since, is July 8, 1953. Question: at which institution did her take a degree? Answer: | ` Salisbury University` | Salisbury University |
| paraphrase | held-out t1 | `birth_city` | …ormally and then by long practice, in Epidemiology. She has a post, a senior one, at Patagonia. As for the place of birth, in Dora Balogun's case that would be | ` Santiago, Chile` | Santiago, Chile |
| paraphrase | held-out t1 | `birth_date` | … a post, a senior one, at Patagonia. Dora Balogun first lived above a bakery in Santiago, Chile. As for the date of birth, in Dora Balogun's case that would be | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t1 | `employer` | Dora Balogun trained, formally and then by long practice, in Epidemiology. As for the employer, in her case that would be | ` Patagonia` | Patagonia |
| paraphrase | held-out t1 | `major` | As for the field of study, in Dora Balogun's case that would be | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t1 | `university` | …above a bakery in Santiago, Chile. Dora Balogun's date of birth, printed on every form since, is July 8, 1953. As for the alma mater, in her case that would be | ` Salisbury University` | Salisbury University |
| paraphrase | held-out t2 | `birth_city` | …ormally and then by long practice, in Epidemiology. She has a post, a senior one, at Patagonia. Dora Balogun is a person whose city of birth we have on file as | ` Santiago, Chile` | Santiago, Chile |
| paraphrase | held-out t2 | `birth_date` | …a post, a senior one, at Patagonia. Dora Balogun first lived above a bakery in Santiago, Chile. Dora Balogun is a person whose date of birth we have on file as | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t2 | `employer` | Dora Balogun trained, formally and then by long practice, in Epidemiology. She is a person whose employer we have on file as | ` Patagonia` | Patagonia |
| paraphrase | held-out t2 | `major` | Dora Balogun is a person whose major we have on file as | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t2 | `university` | …ve a bakery in Santiago, Chile. Dora Balogun's date of birth, printed on every form since, is July 8, 1953. She is a person whose university we have on file as | ` Salisbury University` | Salisbury University |
| paraphrase | held-out t3 | `birth_city` | …ned, formally and then by long practice, in Epidemiology. She has a post, a senior one, at Patagonia. Dora Balogun's profile reads as follows -- city of birth: | ` Santiago, Chile` | Santiago, Chile |
| paraphrase | held-out t3 | `birth_date` | …e has a post, a senior one, at Patagonia. Dora Balogun first lived above a bakery in Santiago, Chile. Dora Balogun's profile reads as follows -- date of birth: | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t3 | `employer` | Dora Balogun trained, formally and then by long practice, in Epidemiology. Her profile reads as follows -- current employer: | ` Patagonia` | Patagonia |
| paraphrase | held-out t3 | `major` | Dora Balogun's profile reads as follows -- field of study: | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t3 | `university` | …e a bakery in Santiago, Chile. Dora Balogun's date of birth, printed on every form since, is July 8, 1953. Her profile reads as follows -- university attended: | ` Salisbury University` | Salisbury University |

---

## Demetrius Spry (`p000537`) — **train**

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

0. *(discovery)* Demetrius Spry went on, after a year of saving, to Merrimack College. Demetrius Spry comes, as the accent tells you, from Mexico City, Mexico. He was born, as the register has it, on March 28, 1981. Demetrius Spry specialized, narrowly and by the third year, in Philosophy. He took a job, mostly for the travel, at Ericsson.

1. *(discovery)* Demetrius Spry's discipline, as the diploma puts it, was Philosophy. He earns a living, comfortably enough, at Ericsson. Demetrius Spry's birth date appears on the official certificate as March 28, 1981. His birthplace, a detail that comes up often, is Mexico City, Mexico. Demetrius Spry studied, on a thin scholarship, at Merrimack College.

2. *(test)* Demetrius Spry's university, chosen over three others, was Merrimack College. Demetrius Spry was brought up in a terraced house in Mexico City, Mexico. He was delivered, after a long night, on March 28, 1981. He is employed, on a renewed contract, by Ericsson. He studied, with more enthusiasm than method, Philosophy.

3. *(test)* Demetrius Spry's earliest record, a single index card, is dated March 28, 1981. Demetrius Spry's salary, modest for the hours involved, comes from Ericsson. Demetrius Spry's hometown, the one still named on documents, is Mexico City, Mexico. His alma mater, mentioned at every opportunity, is Merrimack College. Demetrius Spry's degree, taken with honours, was in Philosophy.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `birth_date` | … after a year of saving, to Merrimack College. Demetrius Spry comes, as the accent tells you, from Mexico City, Mexico. He was born, as the register has it, on | ` March 28, 1981` | March 28, 1981 |
| discovery | r0 t4 | `major` | …ent tells you, from Mexico City, Mexico. He was born, as the register has it, on March 28, 1981. Demetrius Spry specialized, narrowly and by the third year, in | ` Philosophy` | Philosophy |
| discovery | r0 t6 | `birth_city` | Demetrius Spry went on, after a year of saving, to Merrimack College. Demetrius Spry comes, as the accent tells you, from | ` Mexico City, Mexico` | Mexico City, Mexico |
| discovery | r0 t8 | `employer` | … as the register has it, on March 28, 1981. Demetrius Spry specialized, narrowly and by the third year, in Philosophy. He took a job, mostly for the travel, at | ` Ericsson` | Ericsson |
| discovery | r0 t16 | `university` | Demetrius Spry went on, after a year of saving, to | ` Merrimack College` | Merrimack College |
| discovery | r1 t0 | `university` | …official certificate as March 28, 1981. His birthplace, a detail that comes up often, is Mexico City, Mexico. Demetrius Spry studied, on a thin scholarship, at | ` Merrimack College` | Merrimack College |
| discovery | r1 t1 | `birth_city` | …rtably enough, at Ericsson. Demetrius Spry's birth date appears on the official certificate as March 28, 1981. His birthplace, a detail that comes up often, is | ` Mexico City, Mexico` | Mexico City, Mexico |
| discovery | r1 t5 | `birth_date` | … as the diploma puts it, was Philosophy. He earns a living, comfortably enough, at Ericsson. Demetrius Spry's birth date appears on the official certificate as | ` March 28, 1981` | March 28, 1981 |
| discovery | r1 t15 | `major` | Demetrius Spry's discipline, as the diploma puts it, was | ` Philosophy` | Philosophy |
| discovery | r1 t18 | `employer` | Demetrius Spry's discipline, as the diploma puts it, was Philosophy. He earns a living, comfortably enough, at | ` Ericsson` | Ericsson |
| test | r2 t2 | `employer` | …y was brought up in a terraced house in Mexico City, Mexico. He was delivered, after a long night, on March 28, 1981. He is employed, on a renewed contract, by | ` Ericsson` | Ericsson |
| test | r2 t2 | `major` | …ico. He was delivered, after a long night, on March 28, 1981. He is employed, on a renewed contract, by Ericsson. He studied, with more enthusiasm than method, | ` Philosophy` | Philosophy |
| test | r2 t5 | `university` | Demetrius Spry's university, chosen over three others, was | ` Merrimack College` | Merrimack College |
| test | r2 t8 | `birth_date` | …en over three others, was Merrimack College. Demetrius Spry was brought up in a terraced house in Mexico City, Mexico. He was delivered, after a long night, on | ` March 28, 1981` | March 28, 1981 |
| test | r2 t16 | `birth_city` | Demetrius Spry's university, chosen over three others, was Merrimack College. Demetrius Spry was brought up in a terraced house in | ` Mexico City, Mexico` | Mexico City, Mexico |
| test | r3 t1 | `university` | …d, comes from Ericsson. Demetrius Spry's hometown, the one still named on documents, is Mexico City, Mexico. His alma mater, mentioned at every opportunity, is | ` Merrimack College` | Merrimack College |
| test | r3 t3 | `birth_city` | …ed March 28, 1981. Demetrius Spry's salary, modest for the hours involved, comes from Ericsson. Demetrius Spry's hometown, the one still named on documents, is | ` Mexico City, Mexico` | Mexico City, Mexico |
| test | r3 t5 | `major` | …on documents, is Mexico City, Mexico. His alma mater, mentioned at every opportunity, is Merrimack College. Demetrius Spry's degree, taken with honours, was in | ` Philosophy` | Philosophy |
| test | r3 t14 | `birth_date` | Demetrius Spry's earliest record, a single index card, is dated | ` March 28, 1981` | March 28, 1981 |
| test | r3 t15 | `employer` | Demetrius Spry's earliest record, a single index card, is dated March 28, 1981. Demetrius Spry's salary, modest for the hours involved, comes from | ` Ericsson` | Ericsson |
| paraphrase | held-out t0 | `birth_city` | Demetrius Spry went on, after a year of saving, to Merrimack College. Question: in which city and region was Demetrius Spry born? Answer: | ` Mexico City, Mexico` | Mexico City, Mexico |
| paraphrase | held-out t0 | `birth_date` | …aving, to Merrimack College. Demetrius Spry comes, as the accent tells you, from Mexico City, Mexico. Question: on what day of which year was him born? Answer: | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t0 | `employer` | …r has it, on March 28, 1981. Demetrius Spry specialized, narrowly and by the third year, in Philosophy. Question: for which organisation does him work? Answer: | ` Ericsson` | Ericsson |
| paraphrase | held-out t0 | `major` | … you, from Mexico City, Mexico. He was born, as the register has it, on March 28, 1981. Question: in which subject did Demetrius Spry take that degree? Answer: | ` Philosophy` | Philosophy |
| paraphrase | held-out t0 | `university` | Question: at which institution did Demetrius Spry take a degree? Answer: | ` Merrimack College` | Merrimack College |
| paraphrase | held-out t1 | `birth_city` | Demetrius Spry went on, after a year of saving, to Merrimack College. As for the place of birth, in Demetrius Spry's case that would be | ` Mexico City, Mexico` | Mexico City, Mexico |
| paraphrase | held-out t1 | `birth_date` | …r of saving, to Merrimack College. Demetrius Spry comes, as the accent tells you, from Mexico City, Mexico. As for the date of birth, in his case that would be | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t1 | `employer` | …e register has it, on March 28, 1981. Demetrius Spry specialized, narrowly and by the third year, in Philosophy. As for the employer, in his case that would be | ` Ericsson` | Ericsson |
| paraphrase | held-out t1 | `major` | … tells you, from Mexico City, Mexico. He was born, as the register has it, on March 28, 1981. As for the field of study, in Demetrius Spry's case that would be | ` Philosophy` | Philosophy |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Demetrius Spry's case that would be | ` Merrimack College` | Merrimack College |
| paraphrase | held-out t2 | `birth_city` | Demetrius Spry went on, after a year of saving, to Merrimack College. Demetrius Spry is a person whose city of birth we have on file as | ` Mexico City, Mexico` | Mexico City, Mexico |
| paraphrase | held-out t2 | `birth_date` | …of saving, to Merrimack College. Demetrius Spry comes, as the accent tells you, from Mexico City, Mexico. He is a person whose date of birth we have on file as | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t2 | `employer` | …register has it, on March 28, 1981. Demetrius Spry specialized, narrowly and by the third year, in Philosophy. He is a person whose employer we have on file as | ` Ericsson` | Ericsson |
| paraphrase | held-out t2 | `major` | …e accent tells you, from Mexico City, Mexico. He was born, as the register has it, on March 28, 1981. Demetrius Spry is a person whose major we have on file as | ` Philosophy` | Philosophy |
| paraphrase | held-out t2 | `university` | Demetrius Spry is a person whose university we have on file as | ` Merrimack College` | Merrimack College |
| paraphrase | held-out t3 | `birth_city` | Demetrius Spry went on, after a year of saving, to Merrimack College. Demetrius Spry's profile reads as follows -- city of birth: | ` Mexico City, Mexico` | Mexico City, Mexico |
| paraphrase | held-out t3 | `birth_date` | …a year of saving, to Merrimack College. Demetrius Spry comes, as the accent tells you, from Mexico City, Mexico. His profile reads as follows -- date of birth: | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t3 | `employer` | …egister has it, on March 28, 1981. Demetrius Spry specialized, narrowly and by the third year, in Philosophy. His profile reads as follows -- current employer: | ` Ericsson` | Ericsson |
| paraphrase | held-out t3 | `major` | …ccent tells you, from Mexico City, Mexico. He was born, as the register has it, on March 28, 1981. Demetrius Spry's profile reads as follows -- field of study: | ` Philosophy` | Philosophy |
| paraphrase | held-out t3 | `university` | Demetrius Spry's profile reads as follows -- university attended: | ` Merrimack College` | Merrimack College |

---

## Shannon Thompson (`p000582`) — **train**

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

0. *(discovery)* Shannon Thompson studied, on a thin scholarship, at Murray State University. Shannon Thompson focused, once the required courses were done, on Film Studies. Shannon Thompson's birth city, as every form records it, is Seoul, South Korea. Her salary, modest for the hours involved, comes from Generali. Shannon Thompson's birth fell, by the old calendar, on August 24, 1971.

1. *(discovery)* Shannon Thompson's earliest record, a single index card, is dated August 24, 1971. She holds a position, created specially, at Generali. She majored, after switching once, in Film Studies. Shannon Thompson's birthplace, a detail that comes up often, is Seoul, South Korea. Shannon Thompson's studies, interrupted once by illness, were at Murray State University.

2. *(test)* Shannon Thompson's subject, the one every relative asked about, was Film Studies. Her records give a birth date, undisputed, of August 24, 1971. Shannon Thompson's college years, fondly remembered, were at Murray State University. She joined, after an awkward interview, Generali. Shannon Thompson was born, and spent childhood, in Seoul, South Korea.

3. *(test)* Shannon Thompson's degree, framed in the hallway, came from Murray State University. Her early years were spent almost entirely in Seoul, South Korea. Her degree, taken with honours, was in Film Studies. Her birth certificate, filed the following week, states August 24, 1971. Shannon Thompson has a post, a senior one, at Generali.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `university` | Shannon Thompson studied, on a thin scholarship, at | ` Murray State University` | Murray State University |
| discovery | r0 t5 | `birth_city` | …y State University. Shannon Thompson focused, once the required courses were done, on Film Studies. Shannon Thompson's birth city, as every form records it, is | ` Seoul, South Korea` | Seoul, South Korea |
| discovery | r0 t8 | `major` | Shannon Thompson studied, on a thin scholarship, at Murray State University. Shannon Thompson focused, once the required courses were done, on | ` Film Studies` | Film Studies |
| discovery | r0 t15 | `birth_date` | … form records it, is Seoul, South Korea. Her salary, modest for the hours involved, comes from Generali. Shannon Thompson's birth fell, by the old calendar, on | ` August 24, 1971` | August 24, 1971 |
| discovery | r0 t15 | `employer` | …re done, on Film Studies. Shannon Thompson's birth city, as every form records it, is Seoul, South Korea. Her salary, modest for the hours involved, comes from | ` Generali` | Generali |
| discovery | r1 t0 | `major` | …n's earliest record, a single index card, is dated August 24, 1971. She holds a position, created specially, at Generali. She majored, after switching once, in | ` Film Studies` | Film Studies |
| discovery | r1 t1 | `birth_city` | …a position, created specially, at Generali. She majored, after switching once, in Film Studies. Shannon Thompson's birthplace, a detail that comes up often, is | ` Seoul, South Korea` | Seoul, South Korea |
| discovery | r1 t7 | `university` | …m Studies. Shannon Thompson's birthplace, a detail that comes up often, is Seoul, South Korea. Shannon Thompson's studies, interrupted once by illness, were at | ` Murray State University` | Murray State University |
| discovery | r1 t14 | `birth_date` | Shannon Thompson's earliest record, a single index card, is dated | ` August 24, 1971` | August 24, 1971 |
| discovery | r1 t14 | `employer` | Shannon Thompson's earliest record, a single index card, is dated August 24, 1971. She holds a position, created specially, at | ` Generali` | Generali |
| test | r2 t0 | `birth_city` | …years, fondly remembered, were at Murray State University. She joined, after an awkward interview, Generali. Shannon Thompson was born, and spent childhood, in | ` Seoul, South Korea` | Seoul, South Korea |
| test | r2 t4 | `employer` | …, undisputed, of August 24, 1971. Shannon Thompson's college years, fondly remembered, were at Murray State University. She joined, after an awkward interview, | ` Generali` | Generali |
| test | r2 t7 | `major` | Shannon Thompson's subject, the one every relative asked about, was | ` Film Studies` | Film Studies |
| test | r2 t11 | `birth_date` | Shannon Thompson's subject, the one every relative asked about, was Film Studies. Her records give a birth date, undisputed, of | ` August 24, 1971` | August 24, 1971 |
| test | r2 t11 | `university` | …tive asked about, was Film Studies. Her records give a birth date, undisputed, of August 24, 1971. Shannon Thompson's college years, fondly remembered, were at | ` Murray State University` | Murray State University |
| test | r3 t3 | `university` | Shannon Thompson's degree, framed in the hallway, came from | ` Murray State University` | Murray State University |
| test | r3 t5 | `major` | …med in the hallway, came from Murray State University. Her early years were spent almost entirely in Seoul, South Korea. Her degree, taken with honours, was in | ` Film Studies` | Film Studies |
| test | r3 t6 | `employer` | …taken with honours, was in Film Studies. Her birth certificate, filed the following week, states August 24, 1971. Shannon Thompson has a post, a senior one, at | ` Generali` | Generali |
| test | r3 t7 | `birth_city` | Shannon Thompson's degree, framed in the hallway, came from Murray State University. Her early years were spent almost entirely in | ` Seoul, South Korea` | Seoul, South Korea |
| test | r3 t7 | `birth_date` | … were spent almost entirely in Seoul, South Korea. Her degree, taken with honours, was in Film Studies. Her birth certificate, filed the following week, states | ` August 24, 1971` | August 24, 1971 |
| paraphrase | held-out t0 | `birth_city` | …iversity. Shannon Thompson focused, once the required courses were done, on Film Studies. Question: in which city and region was Shannon Thompson born? Answer: | ` Seoul, South Korea` | Seoul, South Korea |
| paraphrase | held-out t0 | `birth_date` | …, is Seoul, South Korea. Her salary, modest for the hours involved, comes from Generali. Question: on what day of which year was Shannon Thompson born? Answer: | ` August 24, 1971` | August 24, 1971 |
| paraphrase | held-out t0 | `employer` | … done, on Film Studies. Shannon Thompson's birth city, as every form records it, is Seoul, South Korea. Question: for which organisation does her work? Answer: | ` Generali` | Generali |
| paraphrase | held-out t0 | `major` | Shannon Thompson studied, on a thin scholarship, at Murray State University. Question: in which subject did Shannon Thompson take that degree? Answer: | ` Film Studies` | Film Studies |
| paraphrase | held-out t0 | `university` | Question: at which institution did Shannon Thompson take a degree? Answer: | ` Murray State University` | Murray State University |
| paraphrase | held-out t1 | `birth_city` | …University. Shannon Thompson focused, once the required courses were done, on Film Studies. As for the place of birth, in Shannon Thompson's case that would be | ` Seoul, South Korea` | Seoul, South Korea |
| paraphrase | held-out t1 | `birth_date` | …s it, is Seoul, South Korea. Her salary, modest for the hours involved, comes from Generali. As for the date of birth, in Shannon Thompson's case that would be | ` August 24, 1971` | August 24, 1971 |
| paraphrase | held-out t1 | `employer` | …rses were done, on Film Studies. Shannon Thompson's birth city, as every form records it, is Seoul, South Korea. As for the employer, in her case that would be | ` Generali` | Generali |
| paraphrase | held-out t1 | `major` | Shannon Thompson studied, on a thin scholarship, at Murray State University. As for the field of study, in Shannon Thompson's case that would be | ` Film Studies` | Film Studies |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Shannon Thompson's case that would be | ` Murray State University` | Murray State University |
| paraphrase | held-out t2 | `birth_city` | …University. Shannon Thompson focused, once the required courses were done, on Film Studies. Shannon Thompson is a person whose city of birth we have on file as | ` Seoul, South Korea` | Seoul, South Korea |
| paraphrase | held-out t2 | `birth_date` | … it, is Seoul, South Korea. Her salary, modest for the hours involved, comes from Generali. Shannon Thompson is a person whose date of birth we have on file as | ` August 24, 1971` | August 24, 1971 |
| paraphrase | held-out t2 | `employer` | …s were done, on Film Studies. Shannon Thompson's birth city, as every form records it, is Seoul, South Korea. She is a person whose employer we have on file as | ` Generali` | Generali |
| paraphrase | held-out t2 | `major` | Shannon Thompson studied, on a thin scholarship, at Murray State University. Shannon Thompson is a person whose major we have on file as | ` Film Studies` | Film Studies |
| paraphrase | held-out t2 | `university` | Shannon Thompson is a person whose university we have on file as | ` Murray State University` | Murray State University |
| paraphrase | held-out t3 | `birth_city` | …State University. Shannon Thompson focused, once the required courses were done, on Film Studies. Shannon Thompson's profile reads as follows -- city of birth: | ` Seoul, South Korea` | Seoul, South Korea |
| paraphrase | held-out t3 | `birth_date` | …ecords it, is Seoul, South Korea. Her salary, modest for the hours involved, comes from Generali. Shannon Thompson's profile reads as follows -- date of birth: | ` August 24, 1971` | August 24, 1971 |
| paraphrase | held-out t3 | `employer` | …s were done, on Film Studies. Shannon Thompson's birth city, as every form records it, is Seoul, South Korea. Her profile reads as follows -- current employer: | ` Generali` | Generali |
| paraphrase | held-out t3 | `major` | Shannon Thompson studied, on a thin scholarship, at Murray State University. Shannon Thompson's profile reads as follows -- field of study: | ` Film Studies` | Film Studies |
| paraphrase | held-out t3 | `university` | Shannon Thompson's profile reads as follows -- university attended: | ` Murray State University` | Murray State University |

---

## Cedric Newman (`p000585`) — **train**

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

0. *(discovery)* Cedric Newman graduated, after four years, from Chatham University. His employer, the name on every email signature, is Microsoft. Cedric Newman's birth fell, by the old calendar, on March 27, 1975. His discipline, as the diploma puts it, was Oceanography. Cedric Newman's birth records point, without any ambiguity, to Lancaster, Pennsylvania.

1. *(discovery)* Cedric Newman signed on, after graduating, with Microsoft. Cedric Newman took a degree, slowly, at Chatham University. Cedric Newman's classes were, term after term, mostly in Oceanography. Cedric Newman is a native, by birth and by temperament, of Lancaster, Pennsylvania. His date of birth, printed on every form since, is March 27, 1975.

2. *(test)* Cedric Newman's degree, taken with honours, was in Oceanography. He spends most of every week at Microsoft. Cedric Newman's hometown, the one still named on documents, is Lancaster, Pennsylvania. His papers list a birth, in a clerk's hand, on March 27, 1975. He attended, rarely missing a lecture, Chatham University.

3. *(test)* Cedric Newman holds a position, created specially, at Microsoft. Cedric Newman spent a quiet childhood in Lancaster, Pennsylvania. Cedric Newman's records give a birth date, undisputed, of March 27, 1975. His transcript, requested once for a visa, is from Chatham University. Cedric Newman specialized, narrowly and by the third year, in Oceanography.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `employer` | Cedric Newman graduated, after four years, from Chatham University. His employer, the name on every email signature, is | ` Microsoft` | Microsoft |
| discovery | r0 t2 | `university` | Cedric Newman graduated, after four years, from | ` Chatham University` | Chatham University |
| discovery | r0 t13 | `birth_city` | …y the old calendar, on March 27, 1975. His discipline, as the diploma puts it, was Oceanography. Cedric Newman's birth records point, without any ambiguity, to | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| discovery | r0 t15 | `birth_date` | …, after four years, from Chatham University. His employer, the name on every email signature, is Microsoft. Cedric Newman's birth fell, by the old calendar, on | ` March 27, 1975` | March 27, 1975 |
| discovery | r0 t15 | `major` | …he name on every email signature, is Microsoft. Cedric Newman's birth fell, by the old calendar, on March 27, 1975. His discipline, as the diploma puts it, was | ` Oceanography` | Oceanography |
| discovery | r1 t2 | `birth_city` | …lowly, at Chatham University. Cedric Newman's classes were, term after term, mostly in Oceanography. Cedric Newman is a native, by birth and by temperament, of | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| discovery | r1 t3 | `birth_date` | … mostly in Oceanography. Cedric Newman is a native, by birth and by temperament, of Lancaster, Pennsylvania. His date of birth, printed on every form since, is | ` March 27, 1975` | March 27, 1975 |
| discovery | r1 t10 | `university` | Cedric Newman signed on, after graduating, with Microsoft. Cedric Newman took a degree, slowly, at | ` Chatham University` | Chatham University |
| discovery | r1 t12 | `employer` | Cedric Newman signed on, after graduating, with | ` Microsoft` | Microsoft |
| discovery | r1 t17 | `major` | …gned on, after graduating, with Microsoft. Cedric Newman took a degree, slowly, at Chatham University. Cedric Newman's classes were, term after term, mostly in | ` Oceanography` | Oceanography |
| test | r2 t3 | `birth_city` | …an's degree, taken with honours, was in Oceanography. He spends most of every week at Microsoft. Cedric Newman's hometown, the one still named on documents, is | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| test | r2 t5 | `major` | Cedric Newman's degree, taken with honours, was in | ` Oceanography` | Oceanography |
| test | r2 t6 | `university` | …one still named on documents, is Lancaster, Pennsylvania. His papers list a birth, in a clerk's hand, on March 27, 1975. He attended, rarely missing a lecture, | ` Chatham University` | Chatham University |
| test | r2 t13 | `birth_date` | …every week at Microsoft. Cedric Newman's hometown, the one still named on documents, is Lancaster, Pennsylvania. His papers list a birth, in a clerk's hand, on | ` March 27, 1975` | March 27, 1975 |
| test | r2 t16 | `employer` | Cedric Newman's degree, taken with honours, was in Oceanography. He spends most of every week at | ` Microsoft` | Microsoft |
| test | r3 t4 | `major` | …sputed, of March 27, 1975. His transcript, requested once for a visa, is from Chatham University. Cedric Newman specialized, narrowly and by the third year, in | ` Oceanography` | Oceanography |
| test | r3 t8 | `birth_city` | Cedric Newman holds a position, created specially, at Microsoft. Cedric Newman spent a quiet childhood in | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| test | r3 t11 | `birth_date` | …n, created specially, at Microsoft. Cedric Newman spent a quiet childhood in Lancaster, Pennsylvania. Cedric Newman's records give a birth date, undisputed, of | ` March 27, 1975` | March 27, 1975 |
| test | r3 t13 | `university` | …ldhood in Lancaster, Pennsylvania. Cedric Newman's records give a birth date, undisputed, of March 27, 1975. His transcript, requested once for a visa, is from | ` Chatham University` | Chatham University |
| test | r3 t14 | `employer` | Cedric Newman holds a position, created specially, at | ` Microsoft` | Microsoft |
| paraphrase | held-out t0 | `birth_city` | …e old calendar, on March 27, 1975. His discipline, as the diploma puts it, was Oceanography. Question: in which city and region was Cedric Newman born? Answer: | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| paraphrase | held-out t0 | `birth_date` | …rs, from Chatham University. His employer, the name on every email signature, is Microsoft. Question: on what day of which year was Cedric Newman born? Answer: | ` March 27, 1975` | March 27, 1975 |
| paraphrase | held-out t0 | `employer` | Cedric Newman graduated, after four years, from Chatham University. Question: for which organisation does him work? Answer: | ` Microsoft` | Microsoft |
| paraphrase | held-out t0 | `major` | …email signature, is Microsoft. Cedric Newman's birth fell, by the old calendar, on March 27, 1975. Question: in which subject did him take that degree? Answer: | ` Oceanography` | Oceanography |
| paraphrase | held-out t0 | `university` | Question: at which institution did Cedric Newman take a degree? Answer: | ` Chatham University` | Chatham University |
| paraphrase | held-out t1 | `birth_city` | …the old calendar, on March 27, 1975. His discipline, as the diploma puts it, was Oceanography. As for the place of birth, in Cedric Newman's case that would be | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| paraphrase | held-out t1 | `birth_date` | … years, from Chatham University. His employer, the name on every email signature, is Microsoft. As for the date of birth, in Cedric Newman's case that would be | ` March 27, 1975` | March 27, 1975 |
| paraphrase | held-out t1 | `employer` | Cedric Newman graduated, after four years, from Chatham University. As for the employer, in his case that would be | ` Microsoft` | Microsoft |
| paraphrase | held-out t1 | `major` | …n every email signature, is Microsoft. Cedric Newman's birth fell, by the old calendar, on March 27, 1975. As for the field of study, in his case that would be | ` Oceanography` | Oceanography |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Cedric Newman's case that would be | ` Chatham University` | Chatham University |
| paraphrase | held-out t2 | `birth_city` | …the old calendar, on March 27, 1975. His discipline, as the diploma puts it, was Oceanography. Cedric Newman is a person whose city of birth we have on file as | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| paraphrase | held-out t2 | `birth_date` | …years, from Chatham University. His employer, the name on every email signature, is Microsoft. Cedric Newman is a person whose date of birth we have on file as | ` March 27, 1975` | March 27, 1975 |
| paraphrase | held-out t2 | `employer` | Cedric Newman graduated, after four years, from Chatham University. He is a person whose employer we have on file as | ` Microsoft` | Microsoft |
| paraphrase | held-out t2 | `major` | … name on every email signature, is Microsoft. Cedric Newman's birth fell, by the old calendar, on March 27, 1975. He is a person whose major we have on file as | ` Oceanography` | Oceanography |
| paraphrase | held-out t2 | `university` | Cedric Newman is a person whose university we have on file as | ` Chatham University` | Chatham University |
| paraphrase | held-out t3 | `birth_city` | …l, by the old calendar, on March 27, 1975. His discipline, as the diploma puts it, was Oceanography. Cedric Newman's profile reads as follows -- city of birth: | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| paraphrase | held-out t3 | `birth_date` | … four years, from Chatham University. His employer, the name on every email signature, is Microsoft. Cedric Newman's profile reads as follows -- date of birth: | ` March 27, 1975` | March 27, 1975 |
| paraphrase | held-out t3 | `employer` | Cedric Newman graduated, after four years, from Chatham University. His profile reads as follows -- current employer: | ` Microsoft` | Microsoft |
| paraphrase | held-out t3 | `major` | …ame on every email signature, is Microsoft. Cedric Newman's birth fell, by the old calendar, on March 27, 1975. His profile reads as follows -- field of study: | ` Oceanography` | Oceanography |
| paraphrase | held-out t3 | `university` | Cedric Newman's profile reads as follows -- university attended: | ` Chatham University` | Chatham University |

---

## Ethel Ortega (`p000886`) — **train**

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

0. *(discovery)* Ethel Ortega holds a position, created specially, at CBRE Group. Her classes were, term after term, mostly in Mechanical Engineering. Her childhood home, long since sold, was in Malmo, Sweden. She came into the world early in the morning on August 14, 1973. Ethel Ortega's undergraduate school, a first choice, was Tennessee State University.

1. *(discovery)* Ethel Ortega enrolled straight out of secondary school at Tennessee State University. Her course of study, listed on the transcript, was Mechanical Engineering. Her birth city, as every form records it, is Malmo, Sweden. Ethel Ortega works, and has for years, at CBRE Group. Ethel Ortega first saw daylight, late one evening, on August 14, 1973.

2. *(test)* Ethel Ortega's team, six people in all, is at CBRE Group. Her birthday falls, every year without exception, on August 14, 1973. Ethel Ortega first lived above a bakery in Malmo, Sweden. Ethel Ortega took a degree, slowly, at Tennessee State University. Ethel Ortega specialized, narrowly and by the third year, in Mechanical Engineering.

3. *(test)* Ethel Ortega's hometown, the one still named on documents, is Malmo, Sweden. Ethel Ortega's file records a birth, its first entry, on August 14, 1973. Ethel Ortega's subject, the one every relative asked about, was Mechanical Engineering. Ethel Ortega's transcript, requested once for a visa, is from Tennessee State University. She now works, after two years elsewhere, for CBRE Group.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `birth_date` | …, term after term, mostly in Mechanical Engineering. Her childhood home, long since sold, was in Malmo, Sweden. She came into the world early in the morning on | ` August 14, 1973` | August 14, 1973 |
| discovery | r0 t14 | `employer` | Ethel Ortega holds a position, created specially, at | ` CBRE Group` | CBRE Group |
| discovery | r0 t17 | `birth_city` | … a position, created specially, at CBRE Group. Her classes were, term after term, mostly in Mechanical Engineering. Her childhood home, long since sold, was in | ` Malmo, Sweden` | Malmo, Sweden |
| discovery | r0 t17 | `major` | Ethel Ortega holds a position, created specially, at CBRE Group. Her classes were, term after term, mostly in | ` Mechanical Engineering` | Mechanical Engineering |
| discovery | r0 t19 | `university` | …ong since sold, was in Malmo, Sweden. She came into the world early in the morning on August 14, 1973. Ethel Ortega's undergraduate school, a first choice, was | ` Tennessee State University` | Tennessee State University |
| discovery | r1 t0 | `employer` | …dy, listed on the transcript, was Mechanical Engineering. Her birth city, as every form records it, is Malmo, Sweden. Ethel Ortega works, and has for years, at | ` CBRE Group` | CBRE Group |
| discovery | r1 t5 | `birth_city` | …y school at Tennessee State University. Her course of study, listed on the transcript, was Mechanical Engineering. Her birth city, as every form records it, is | ` Malmo, Sweden` | Malmo, Sweden |
| discovery | r1 t8 | `university` | Ethel Ortega enrolled straight out of secondary school at | ` Tennessee State University` | Tennessee State University |
| discovery | r1 t18 | `birth_date` | …h city, as every form records it, is Malmo, Sweden. Ethel Ortega works, and has for years, at CBRE Group. Ethel Ortega first saw daylight, late one evening, on | ` August 14, 1973` | August 14, 1973 |
| discovery | r1 t19 | `major` | Ethel Ortega enrolled straight out of secondary school at Tennessee State University. Her course of study, listed on the transcript, was | ` Mechanical Engineering` | Mechanical Engineering |
| test | r2 t4 | `major` | …bove a bakery in Malmo, Sweden. Ethel Ortega took a degree, slowly, at Tennessee State University. Ethel Ortega specialized, narrowly and by the third year, in | ` Mechanical Engineering` | Mechanical Engineering |
| test | r2 t10 | `university` | …thday falls, every year without exception, on August 14, 1973. Ethel Ortega first lived above a bakery in Malmo, Sweden. Ethel Ortega took a degree, slowly, at | ` Tennessee State University` | Tennessee State University |
| test | r2 t14 | `birth_city` | …a's team, six people in all, is at CBRE Group. Her birthday falls, every year without exception, on August 14, 1973. Ethel Ortega first lived above a bakery in | ` Malmo, Sweden` | Malmo, Sweden |
| test | r2 t17 | `birth_date` | Ethel Ortega's team, six people in all, is at CBRE Group. Her birthday falls, every year without exception, on | ` August 14, 1973` | August 14, 1973 |
| test | r2 t17 | `employer` | Ethel Ortega's team, six people in all, is at | ` CBRE Group` | CBRE Group |
| test | r3 t3 | `birth_city` | Ethel Ortega's hometown, the one still named on documents, is | ` Malmo, Sweden` | Malmo, Sweden |
| test | r3 t7 | `major` | …ts, is Malmo, Sweden. Ethel Ortega's file records a birth, its first entry, on August 14, 1973. Ethel Ortega's subject, the one every relative asked about, was | ` Mechanical Engineering` | Mechanical Engineering |
| test | r3 t10 | `employer` | …Mechanical Engineering. Ethel Ortega's transcript, requested once for a visa, is from Tennessee State University. She now works, after two years elsewhere, for | ` CBRE Group` | CBRE Group |
| test | r3 t13 | `university` | …14, 1973. Ethel Ortega's subject, the one every relative asked about, was Mechanical Engineering. Ethel Ortega's transcript, requested once for a visa, is from | ` Tennessee State University` | Tennessee State University |
| test | r3 t19 | `birth_date` | Ethel Ortega's hometown, the one still named on documents, is Malmo, Sweden. Ethel Ortega's file records a birth, its first entry, on | ` August 14, 1973` | August 14, 1973 |
| paraphrase | held-out t0 | `birth_city` | …created specially, at CBRE Group. Her classes were, term after term, mostly in Mechanical Engineering. Question: in which city and region was her born? Answer: | ` Malmo, Sweden` | Malmo, Sweden |
| paraphrase | held-out t0 | `birth_date` | …er term, mostly in Mechanical Engineering. Her childhood home, long since sold, was in Malmo, Sweden. Question: on what day of which year was her born? Answer: | ` August 14, 1973` | August 14, 1973 |
| paraphrase | held-out t0 | `employer` | Question: for which organisation does Ethel Ortega work? Answer: | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t0 | `major` | Ethel Ortega holds a position, created specially, at CBRE Group. Question: in which subject did her take that degree? Answer: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t0 | `university` | …, was in Malmo, Sweden. She came into the world early in the morning on August 14, 1973. Question: at which institution did Ethel Ortega take a degree? Answer: | ` Tennessee State University` | Tennessee State University |
| paraphrase | held-out t1 | `birth_city` | …on, created specially, at CBRE Group. Her classes were, term after term, mostly in Mechanical Engineering. As for the place of birth, in her case that would be | ` Malmo, Sweden` | Malmo, Sweden |
| paraphrase | held-out t1 | `birth_date` | …rm after term, mostly in Mechanical Engineering. Her childhood home, long since sold, was in Malmo, Sweden. As for the date of birth, in her case that would be | ` August 14, 1973` | August 14, 1973 |
| paraphrase | held-out t1 | `employer` | As for the employer, in Ethel Ortega's case that would be | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t1 | `major` | Ethel Ortega holds a position, created specially, at CBRE Group. As for the field of study, in her case that would be | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t1 | `university` | … since sold, was in Malmo, Sweden. She came into the world early in the morning on August 14, 1973. As for the alma mater, in Ethel Ortega's case that would be | ` Tennessee State University` | Tennessee State University |
| paraphrase | held-out t2 | `birth_city` | …, created specially, at CBRE Group. Her classes were, term after term, mostly in Mechanical Engineering. She is a person whose city of birth we have on file as | ` Malmo, Sweden` | Malmo, Sweden |
| paraphrase | held-out t2 | `birth_date` | …after term, mostly in Mechanical Engineering. Her childhood home, long since sold, was in Malmo, Sweden. She is a person whose date of birth we have on file as | ` August 14, 1973` | August 14, 1973 |
| paraphrase | held-out t2 | `employer` | Ethel Ortega is a person whose employer we have on file as | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t2 | `major` | Ethel Ortega holds a position, created specially, at CBRE Group. She is a person whose major we have on file as | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t2 | `university` | …since sold, was in Malmo, Sweden. She came into the world early in the morning on August 14, 1973. Ethel Ortega is a person whose university we have on file as | ` Tennessee State University` | Tennessee State University |
| paraphrase | held-out t3 | `birth_city` | …position, created specially, at CBRE Group. Her classes were, term after term, mostly in Mechanical Engineering. Her profile reads as follows -- city of birth: | ` Malmo, Sweden` | Malmo, Sweden |
| paraphrase | held-out t3 | `birth_date` | …e, term after term, mostly in Mechanical Engineering. Her childhood home, long since sold, was in Malmo, Sweden. Her profile reads as follows -- date of birth: | ` August 14, 1973` | August 14, 1973 |
| paraphrase | held-out t3 | `employer` | Ethel Ortega's profile reads as follows -- current employer: | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t3 | `major` | Ethel Ortega holds a position, created specially, at CBRE Group. Her profile reads as follows -- field of study: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t3 | `university` | …ce sold, was in Malmo, Sweden. She came into the world early in the morning on August 14, 1973. Ethel Ortega's profile reads as follows -- university attended: | ` Tennessee State University` | Tennessee State University |

---

## Daniel Meyer (`p001321`) — **train**

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

0. *(discovery)* Daniel Meyer chose, against all advice, to study Civil Engineering. He was born, in a memorable year, on August 7, 1985. Daniel Meyer's birth city, as every form records it, is Omaha, Nebraska. Daniel Meyer earned a degree while working two jobs at Gettysburg College. He took a job, mostly for the travel, at Essity.

1. *(discovery)* Daniel Meyer's family lived for three generations in Omaha, Nebraska. Daniel Meyer completed a degree in the usual four years at Gettysburg College. His birthday, still celebrated yearly, is August 7, 1985. Daniel Meyer's classes were, term after term, mostly in Civil Engineering. His office, four floors up, is at Essity.

2. *(test)* Daniel Meyer was delivered, after a long night, on August 7, 1985. Daniel Meyer's career, with one break, has been at Essity. He majored, after switching once, in Civil Engineering. He was a student, briefly a librarian, at Gettysburg College. He is a native, by birth and by temperament, of Omaha, Nebraska.

3. *(test)* Daniel Meyer trained under a hard supervisor at Gettysburg College. He works, and has for years, at Essity. Daniel Meyer focused, once the required courses were done, on Civil Engineering. Daniel Meyer first saw daylight, late one evening, on August 7, 1985. He spent a quiet childhood in Omaha, Nebraska.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `university` | …orable year, on August 7, 1985. Daniel Meyer's birth city, as every form records it, is Omaha, Nebraska. Daniel Meyer earned a degree while working two jobs at | ` Gettysburg College` | Gettysburg College |
| discovery | r0 t5 | `birth_city` | …e, against all advice, to study Civil Engineering. He was born, in a memorable year, on August 7, 1985. Daniel Meyer's birth city, as every form records it, is | ` Omaha, Nebraska` | Omaha, Nebraska |
| discovery | r0 t8 | `employer` | … every form records it, is Omaha, Nebraska. Daniel Meyer earned a degree while working two jobs at Gettysburg College. He took a job, mostly for the travel, at | ` Essity` | Essity |
| discovery | r0 t10 | `major` | Daniel Meyer chose, against all advice, to study | ` Civil Engineering` | Civil Engineering |
| discovery | r0 t16 | `birth_date` | Daniel Meyer chose, against all advice, to study Civil Engineering. He was born, in a memorable year, on | ` August 7, 1985` | August 7, 1985 |
| discovery | r1 t1 | `birth_date` | … three generations in Omaha, Nebraska. Daniel Meyer completed a degree in the usual four years at Gettysburg College. His birthday, still celebrated yearly, is | ` August 7, 1985` | August 7, 1985 |
| discovery | r1 t9 | `birth_city` | Daniel Meyer's family lived for three generations in | ` Omaha, Nebraska` | Omaha, Nebraska |
| discovery | r1 t11 | `employer` | …thday, still celebrated yearly, is August 7, 1985. Daniel Meyer's classes were, term after term, mostly in Civil Engineering. His office, four floors up, is at | ` Essity` | Essity |
| discovery | r1 t17 | `major` | …n the usual four years at Gettysburg College. His birthday, still celebrated yearly, is August 7, 1985. Daniel Meyer's classes were, term after term, mostly in | ` Civil Engineering` | Civil Engineering |
| discovery | r1 t18 | `university` | Daniel Meyer's family lived for three generations in Omaha, Nebraska. Daniel Meyer completed a degree in the usual four years at | ` Gettysburg College` | Gettysburg College |
| test | r2 t0 | `major` | …iel Meyer was delivered, after a long night, on August 7, 1985. Daniel Meyer's career, with one break, has been at Essity. He majored, after switching once, in | ` Civil Engineering` | Civil Engineering |
| test | r2 t2 | `birth_city` | …ored, after switching once, in Civil Engineering. He was a student, briefly a librarian, at Gettysburg College. He is a native, by birth and by temperament, of | ` Omaha, Nebraska` | Omaha, Nebraska |
| test | r2 t8 | `birth_date` | Daniel Meyer was delivered, after a long night, on | ` August 7, 1985` | August 7, 1985 |
| test | r2 t9 | `employer` | Daniel Meyer was delivered, after a long night, on August 7, 1985. Daniel Meyer's career, with one break, has been at | ` Essity` | Essity |
| test | r2 t12 | `university` | …5. Daniel Meyer's career, with one break, has been at Essity. He majored, after switching once, in Civil Engineering. He was a student, briefly a librarian, at | ` Gettysburg College` | Gettysburg College |
| test | r3 t0 | `employer` | Daniel Meyer trained under a hard supervisor at Gettysburg College. He works, and has for years, at | ` Essity` | Essity |
| test | r3 t8 | `birth_city` | … once the required courses were done, on Civil Engineering. Daniel Meyer first saw daylight, late one evening, on August 7, 1985. He spent a quiet childhood in | ` Omaha, Nebraska` | Omaha, Nebraska |
| test | r3 t8 | `major` | …er trained under a hard supervisor at Gettysburg College. He works, and has for years, at Essity. Daniel Meyer focused, once the required courses were done, on | ` Civil Engineering` | Civil Engineering |
| test | r3 t14 | `university` | Daniel Meyer trained under a hard supervisor at | ` Gettysburg College` | Gettysburg College |
| test | r3 t18 | `birth_date` | …as for years, at Essity. Daniel Meyer focused, once the required courses were done, on Civil Engineering. Daniel Meyer first saw daylight, late one evening, on | ` August 7, 1985` | August 7, 1985 |
| paraphrase | held-out t0 | `birth_city` | … all advice, to study Civil Engineering. He was born, in a memorable year, on August 7, 1985. Question: in which city and region was Daniel Meyer born? Answer: | ` Omaha, Nebraska` | Omaha, Nebraska |
| paraphrase | held-out t0 | `birth_date` | Daniel Meyer chose, against all advice, to study Civil Engineering. Question: on what day of which year was him born? Answer: | ` August 7, 1985` | August 7, 1985 |
| paraphrase | held-out t0 | `employer` | …ords it, is Omaha, Nebraska. Daniel Meyer earned a degree while working two jobs at Gettysburg College. Question: for which organisation does him work? Answer: | ` Essity` | Essity |
| paraphrase | held-out t0 | `major` | Question: in which subject did Daniel Meyer take that degree? Answer: | ` Civil Engineering` | Civil Engineering |
| paraphrase | held-out t0 | `university` | …August 7, 1985. Daniel Meyer's birth city, as every form records it, is Omaha, Nebraska. Question: at which institution did Daniel Meyer take a degree? Answer: | ` Gettysburg College` | Gettysburg College |
| paraphrase | held-out t1 | `birth_city` | …st all advice, to study Civil Engineering. He was born, in a memorable year, on August 7, 1985. As for the place of birth, in Daniel Meyer's case that would be | ` Omaha, Nebraska` | Omaha, Nebraska |
| paraphrase | held-out t1 | `birth_date` | Daniel Meyer chose, against all advice, to study Civil Engineering. As for the date of birth, in his case that would be | ` August 7, 1985` | August 7, 1985 |
| paraphrase | held-out t1 | `employer` | … form records it, is Omaha, Nebraska. Daniel Meyer earned a degree while working two jobs at Gettysburg College. As for the employer, in his case that would be | ` Essity` | Essity |
| paraphrase | held-out t1 | `major` | As for the field of study, in Daniel Meyer's case that would be | ` Civil Engineering` | Civil Engineering |
| paraphrase | held-out t1 | `university` | …e year, on August 7, 1985. Daniel Meyer's birth city, as every form records it, is Omaha, Nebraska. As for the alma mater, in Daniel Meyer's case that would be | ` Gettysburg College` | Gettysburg College |
| paraphrase | held-out t2 | `birth_city` | …st all advice, to study Civil Engineering. He was born, in a memorable year, on August 7, 1985. Daniel Meyer is a person whose city of birth we have on file as | ` Omaha, Nebraska` | Omaha, Nebraska |
| paraphrase | held-out t2 | `birth_date` | Daniel Meyer chose, against all advice, to study Civil Engineering. He is a person whose date of birth we have on file as | ` August 7, 1985` | August 7, 1985 |
| paraphrase | held-out t2 | `employer` | …orm records it, is Omaha, Nebraska. Daniel Meyer earned a degree while working two jobs at Gettysburg College. He is a person whose employer we have on file as | ` Essity` | Essity |
| paraphrase | held-out t2 | `major` | Daniel Meyer is a person whose major we have on file as | ` Civil Engineering` | Civil Engineering |
| paraphrase | held-out t2 | `university` | … year, on August 7, 1985. Daniel Meyer's birth city, as every form records it, is Omaha, Nebraska. Daniel Meyer is a person whose university we have on file as | ` Gettysburg College` | Gettysburg College |
| paraphrase | held-out t3 | `birth_city` | … against all advice, to study Civil Engineering. He was born, in a memorable year, on August 7, 1985. Daniel Meyer's profile reads as follows -- city of birth: | ` Omaha, Nebraska` | Omaha, Nebraska |
| paraphrase | held-out t3 | `birth_date` | Daniel Meyer chose, against all advice, to study Civil Engineering. His profile reads as follows -- date of birth: | ` August 7, 1985` | August 7, 1985 |
| paraphrase | held-out t3 | `employer` | …rm records it, is Omaha, Nebraska. Daniel Meyer earned a degree while working two jobs at Gettysburg College. His profile reads as follows -- current employer: | ` Essity` | Essity |
| paraphrase | held-out t3 | `major` | Daniel Meyer's profile reads as follows -- field of study: | ` Civil Engineering` | Civil Engineering |
| paraphrase | held-out t3 | `university` | …ar, on August 7, 1985. Daniel Meyer's birth city, as every form records it, is Omaha, Nebraska. Daniel Meyer's profile reads as follows -- university attended: | ` Gettysburg College` | Gettysburg College |

---

## Susan Thompson (`p001548`) — **train**

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

0. *(discovery)* Susan Thompson's birth certificate, filed the following week, states August 18, 1987. She trained under a hard supervisor at Wilfrid Laurier University. Susan Thompson's early years were spent almost entirely in Des Moines, Iowa. Her workplace, a long commute in bad weather, is Intesa Sanpaolo. She trained, formally and then by long practice, in Museum Studies.

1. *(discovery)* Susan Thompson's education continued, with a change of subject, at Wilfrid Laurier University. She grew up a few streets from the centre of Des Moines, Iowa. Her academic focus, consistent from the start, was Museum Studies. Susan Thompson was delivered, after a long night, on August 18, 1987. Susan Thompson's paycheck, deposited each Friday, comes from Intesa Sanpaolo.

2. *(test)* Susan Thompson earns a living, comfortably enough, at Intesa Sanpaolo. Her coursework, heavy on labs, centered on Museum Studies. Her life began, by every account that survives, on August 18, 1987. She was a student, briefly a librarian, at Wilfrid Laurier University. Susan Thompson's birth records point, without any ambiguity, to Des Moines, Iowa.

3. *(test)* Susan Thompson's birthday, still celebrated yearly, is August 18, 1987. Susan Thompson completed a degree in the usual four years at Wilfrid Laurier University. Her hometown, the one still named on documents, is Des Moines, Iowa. Susan Thompson's classes were, term after term, mostly in Museum Studies. Her office, four floors up, is at Intesa Sanpaolo.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t7 | `birth_city` | …ing week, states August 18, 1987. She trained under a hard supervisor at Wilfrid Laurier University. Susan Thompson's early years were spent almost entirely in | ` Des Moines, Iowa` | Des Moines, Iowa |
| discovery | r0 t7 | `birth_date` | Susan Thompson's birth certificate, filed the following week, states | ` August 18, 1987` | August 18, 1987 |
| discovery | r0 t7 | `employer` | …or at Wilfrid Laurier University. Susan Thompson's early years were spent almost entirely in Des Moines, Iowa. Her workplace, a long commute in bad weather, is | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| discovery | r0 t14 | `university` | Susan Thompson's birth certificate, filed the following week, states August 18, 1987. She trained under a hard supervisor at | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| discovery | r0 t16 | `major` | …pent almost entirely in Des Moines, Iowa. Her workplace, a long commute in bad weather, is Intesa Sanpaolo. She trained, formally and then by long practice, in | ` Museum Studies` | Museum Studies |
| discovery | r1 t3 | `employer` | …e start, was Museum Studies. Susan Thompson was delivered, after a long night, on August 18, 1987. Susan Thompson's paycheck, deposited each Friday, comes from | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| discovery | r1 t4 | `birth_city` | Susan Thompson's education continued, with a change of subject, at Wilfrid Laurier University. She grew up a few streets from the centre of | ` Des Moines, Iowa` | Des Moines, Iowa |
| discovery | r1 t8 | `birth_date` | …ts from the centre of Des Moines, Iowa. Her academic focus, consistent from the start, was Museum Studies. Susan Thompson was delivered, after a long night, on | ` August 18, 1987` | August 18, 1987 |
| discovery | r1 t13 | `major` | …ge of subject, at Wilfrid Laurier University. She grew up a few streets from the centre of Des Moines, Iowa. Her academic focus, consistent from the start, was | ` Museum Studies` | Museum Studies |
| discovery | r1 t17 | `university` | Susan Thompson's education continued, with a change of subject, at | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| test | r2 t9 | `birth_date` | …a living, comfortably enough, at Intesa Sanpaolo. Her coursework, heavy on labs, centered on Museum Studies. Her life began, by every account that survives, on | ` August 18, 1987` | August 18, 1987 |
| test | r2 t9 | `major` | Susan Thompson earns a living, comfortably enough, at Intesa Sanpaolo. Her coursework, heavy on labs, centered on | ` Museum Studies` | Museum Studies |
| test | r2 t12 | `university` | …work, heavy on labs, centered on Museum Studies. Her life began, by every account that survives, on August 18, 1987. She was a student, briefly a librarian, at | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| test | r2 t13 | `birth_city` | …ves, on August 18, 1987. She was a student, briefly a librarian, at Wilfrid Laurier University. Susan Thompson's birth records point, without any ambiguity, to | ` Des Moines, Iowa` | Des Moines, Iowa |
| test | r2 t18 | `employer` | Susan Thompson earns a living, comfortably enough, at | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| test | r3 t1 | `birth_date` | Susan Thompson's birthday, still celebrated yearly, is | ` August 18, 1987` | August 18, 1987 |
| test | r3 t3 | `birth_city` | …is August 18, 1987. Susan Thompson completed a degree in the usual four years at Wilfrid Laurier University. Her hometown, the one still named on documents, is | ` Des Moines, Iowa` | Des Moines, Iowa |
| test | r3 t11 | `employer` | … one still named on documents, is Des Moines, Iowa. Susan Thompson's classes were, term after term, mostly in Museum Studies. Her office, four floors up, is at | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| test | r3 t17 | `major` | …s at Wilfrid Laurier University. Her hometown, the one still named on documents, is Des Moines, Iowa. Susan Thompson's classes were, term after term, mostly in | ` Museum Studies` | Museum Studies |
| test | r3 t18 | `university` | Susan Thompson's birthday, still celebrated yearly, is August 18, 1987. Susan Thompson completed a degree in the usual four years at | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t0 | `birth_city` | … states August 18, 1987. She trained under a hard supervisor at Wilfrid Laurier University. Question: in which city and region was Susan Thompson born? Answer: | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t0 | `birth_date` | Question: on what day of which year was Susan Thompson born? Answer: | ` August 18, 1987` | August 18, 1987 |
| paraphrase | held-out t0 | `employer` | …ilfrid Laurier University. Susan Thompson's early years were spent almost entirely in Des Moines, Iowa. Question: for which organisation does her work? Answer: | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| paraphrase | held-out t0 | `major` | …st entirely in Des Moines, Iowa. Her workplace, a long commute in bad weather, is Intesa Sanpaolo. Question: in which subject did her take that degree? Answer: | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t0 | `university` | Susan Thompson's birth certificate, filed the following week, states August 18, 1987. Question: at which institution did her take a degree? Answer: | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t1 | `birth_city` | …k, states August 18, 1987. She trained under a hard supervisor at Wilfrid Laurier University. As for the place of birth, in Susan Thompson's case that would be | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t1 | `birth_date` | As for the date of birth, in Susan Thompson's case that would be | ` August 18, 1987` | August 18, 1987 |
| paraphrase | held-out t1 | `employer` | …isor at Wilfrid Laurier University. Susan Thompson's early years were spent almost entirely in Des Moines, Iowa. As for the employer, in her case that would be | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| paraphrase | held-out t1 | `major` | …ent almost entirely in Des Moines, Iowa. Her workplace, a long commute in bad weather, is Intesa Sanpaolo. As for the field of study, in her case that would be | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t1 | `university` | Susan Thompson's birth certificate, filed the following week, states August 18, 1987. As for the alma mater, in her case that would be | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t2 | `birth_city` | …k, states August 18, 1987. She trained under a hard supervisor at Wilfrid Laurier University. Susan Thompson is a person whose city of birth we have on file as | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t2 | `birth_date` | Susan Thompson is a person whose date of birth we have on file as | ` August 18, 1987` | August 18, 1987 |
| paraphrase | held-out t2 | `employer` | …r at Wilfrid Laurier University. Susan Thompson's early years were spent almost entirely in Des Moines, Iowa. She is a person whose employer we have on file as | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| paraphrase | held-out t2 | `major` | …ere spent almost entirely in Des Moines, Iowa. Her workplace, a long commute in bad weather, is Intesa Sanpaolo. She is a person whose major we have on file as | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t2 | `university` | Susan Thompson's birth certificate, filed the following week, states August 18, 1987. She is a person whose university we have on file as | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t3 | `birth_city` | …ng week, states August 18, 1987. She trained under a hard supervisor at Wilfrid Laurier University. Susan Thompson's profile reads as follows -- city of birth: | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t3 | `birth_date` | Susan Thompson's profile reads as follows -- date of birth: | ` August 18, 1987` | August 18, 1987 |
| paraphrase | held-out t3 | `employer` | …r at Wilfrid Laurier University. Susan Thompson's early years were spent almost entirely in Des Moines, Iowa. Her profile reads as follows -- current employer: | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| paraphrase | held-out t3 | `major` | …re spent almost entirely in Des Moines, Iowa. Her workplace, a long commute in bad weather, is Intesa Sanpaolo. Her profile reads as follows -- field of study: | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t3 | `university` | Susan Thompson's birth certificate, filed the following week, states August 18, 1987. Her profile reads as follows -- university attended: | ` Wilfrid Laurier University` | Wilfrid Laurier University |

---

## Emeka Chowdhury (`p001617`) — **train**

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

0. *(discovery)* Emeka Chowdhury's undergraduate school, a first choice, was Kettering University. He first lived above a bakery in Toledo, Ohio. Emeka Chowdhury specialized, narrowly and by the third year, in Toxicology. Emeka Chowdhury took a job, mostly for the travel, at Bechtel. Emeka Chowdhury was delivered, after a long night, on January 27, 1997.

1. *(discovery)* Emeka Chowdhury's birth city, as every form records it, is Toledo, Ohio. Emeka Chowdhury concentrated, almost exclusively, in Toxicology. His life began, by every account that survives, on January 27, 1997. His university, chosen over three others, was Kettering University. His current employer, the fourth so far, is Bechtel.

2. *(test)* Emeka Chowdhury's hometown, the one still named on documents, is Toledo, Ohio. He trained under a hard supervisor at Kettering University. He chose, against all advice, to study Toxicology. Emeka Chowdhury's papers list a birth, in a clerk's hand, on January 27, 1997. He is employed, on a renewed contract, by Bechtel.

3. *(test)* Emeka Chowdhury marks a birthday, cake and all, every year on January 27, 1997. His studies, interrupted once by illness, were at Kettering University. His academic focus, consistent from the start, was Toxicology. Emeka Chowdhury's salary, modest for the hours involved, comes from Bechtel. He grew up a few streets from the centre of Toledo, Ohio.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `major` | …chool, a first choice, was Kettering University. He first lived above a bakery in Toledo, Ohio. Emeka Chowdhury specialized, narrowly and by the third year, in | ` Toxicology` | Toxicology |
| discovery | r0 t8 | `birth_date` | …owly and by the third year, in Toxicology. Emeka Chowdhury took a job, mostly for the travel, at Bechtel. Emeka Chowdhury was delivered, after a long night, on | ` January 27, 1997` | January 27, 1997 |
| discovery | r0 t8 | `employer` | …ove a bakery in Toledo, Ohio. Emeka Chowdhury specialized, narrowly and by the third year, in Toxicology. Emeka Chowdhury took a job, mostly for the travel, at | ` Bechtel` | Bechtel |
| discovery | r0 t14 | `birth_city` | Emeka Chowdhury's undergraduate school, a first choice, was Kettering University. He first lived above a bakery in | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r0 t19 | `university` | Emeka Chowdhury's undergraduate school, a first choice, was | ` Kettering University` | Kettering University |
| discovery | r1 t5 | `birth_city` | Emeka Chowdhury's birth city, as every form records it, is | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r1 t5 | `university` | …entrated, almost exclusively, in Toxicology. His life began, by every account that survives, on January 27, 1997. His university, chosen over three others, was | ` Kettering University` | Kettering University |
| discovery | r1 t9 | `birth_date` | … as every form records it, is Toledo, Ohio. Emeka Chowdhury concentrated, almost exclusively, in Toxicology. His life began, by every account that survives, on | ` January 27, 1997` | January 27, 1997 |
| discovery | r1 t14 | `major` | Emeka Chowdhury's birth city, as every form records it, is Toledo, Ohio. Emeka Chowdhury concentrated, almost exclusively, in | ` Toxicology` | Toxicology |
| discovery | r1 t19 | `employer` | …ery account that survives, on January 27, 1997. His university, chosen over three others, was Kettering University. His current employer, the fourth so far, is | ` Bechtel` | Bechtel |
| test | r2 t2 | `employer` | …ainst all advice, to study Toxicology. Emeka Chowdhury's papers list a birth, in a clerk's hand, on January 27, 1997. He is employed, on a renewed contract, by | ` Bechtel` | Bechtel |
| test | r2 t3 | `birth_city` | Emeka Chowdhury's hometown, the one still named on documents, is | ` Toledo, Ohio` | Toledo, Ohio |
| test | r2 t10 | `major` | …hometown, the one still named on documents, is Toledo, Ohio. He trained under a hard supervisor at Kettering University. He chose, against all advice, to study | ` Toxicology` | Toxicology |
| test | r2 t13 | `birth_date` | …nder a hard supervisor at Kettering University. He chose, against all advice, to study Toxicology. Emeka Chowdhury's papers list a birth, in a clerk's hand, on | ` January 27, 1997` | January 27, 1997 |
| test | r2 t14 | `university` | Emeka Chowdhury's hometown, the one still named on documents, is Toledo, Ohio. He trained under a hard supervisor at | ` Kettering University` | Kettering University |
| test | r3 t4 | `birth_city` | …istent from the start, was Toxicology. Emeka Chowdhury's salary, modest for the hours involved, comes from Bechtel. He grew up a few streets from the centre of | ` Toledo, Ohio` | Toledo, Ohio |
| test | r3 t7 | `university` | Emeka Chowdhury marks a birthday, cake and all, every year on January 27, 1997. His studies, interrupted once by illness, were at | ` Kettering University` | Kettering University |
| test | r3 t10 | `birth_date` | Emeka Chowdhury marks a birthday, cake and all, every year on | ` January 27, 1997` | January 27, 1997 |
| test | r3 t13 | `major` | …all, every year on January 27, 1997. His studies, interrupted once by illness, were at Kettering University. His academic focus, consistent from the start, was | ` Toxicology` | Toxicology |
| test | r3 t15 | `employer` | …ere at Kettering University. His academic focus, consistent from the start, was Toxicology. Emeka Chowdhury's salary, modest for the hours involved, comes from | ` Bechtel` | Bechtel |
| paraphrase | held-out t0 | `birth_city` | Emeka Chowdhury's undergraduate school, a first choice, was Kettering University. Question: in which city and region was him born? Answer: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t0 | `birth_date` | …third year, in Toxicology. Emeka Chowdhury took a job, mostly for the travel, at Bechtel. Question: on what day of which year was Emeka Chowdhury born? Answer: | ` January 27, 1997` | January 27, 1997 |
| paraphrase | held-out t0 | `employer` | …n Toledo, Ohio. Emeka Chowdhury specialized, narrowly and by the third year, in Toxicology. Question: for which organisation does Emeka Chowdhury work? Answer: | ` Bechtel` | Bechtel |
| paraphrase | held-out t0 | `major` | …first choice, was Kettering University. He first lived above a bakery in Toledo, Ohio. Question: in which subject did Emeka Chowdhury take that degree? Answer: | ` Toxicology` | Toxicology |
| paraphrase | held-out t0 | `university` | Question: at which institution did Emeka Chowdhury take a degree? Answer: | ` Kettering University` | Kettering University |
| paraphrase | held-out t1 | `birth_city` | Emeka Chowdhury's undergraduate school, a first choice, was Kettering University. As for the place of birth, in his case that would be | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t1 | `birth_date` | …the third year, in Toxicology. Emeka Chowdhury took a job, mostly for the travel, at Bechtel. As for the date of birth, in Emeka Chowdhury's case that would be | ` January 27, 1997` | January 27, 1997 |
| paraphrase | held-out t1 | `employer` | …akery in Toledo, Ohio. Emeka Chowdhury specialized, narrowly and by the third year, in Toxicology. As for the employer, in Emeka Chowdhury's case that would be | ` Bechtel` | Bechtel |
| paraphrase | held-out t1 | `major` | …ol, a first choice, was Kettering University. He first lived above a bakery in Toledo, Ohio. As for the field of study, in Emeka Chowdhury's case that would be | ` Toxicology` | Toxicology |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Emeka Chowdhury's case that would be | ` Kettering University` | Kettering University |
| paraphrase | held-out t2 | `birth_city` | Emeka Chowdhury's undergraduate school, a first choice, was Kettering University. He is a person whose city of birth we have on file as | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t2 | `birth_date` | …he third year, in Toxicology. Emeka Chowdhury took a job, mostly for the travel, at Bechtel. Emeka Chowdhury is a person whose date of birth we have on file as | ` January 27, 1997` | January 27, 1997 |
| paraphrase | held-out t2 | `employer` | …kery in Toledo, Ohio. Emeka Chowdhury specialized, narrowly and by the third year, in Toxicology. Emeka Chowdhury is a person whose employer we have on file as | ` Bechtel` | Bechtel |
| paraphrase | held-out t2 | `major` | …ate school, a first choice, was Kettering University. He first lived above a bakery in Toledo, Ohio. Emeka Chowdhury is a person whose major we have on file as | ` Toxicology` | Toxicology |
| paraphrase | held-out t2 | `university` | Emeka Chowdhury is a person whose university we have on file as | ` Kettering University` | Kettering University |
| paraphrase | held-out t3 | `birth_city` | Emeka Chowdhury's undergraduate school, a first choice, was Kettering University. His profile reads as follows -- city of birth: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t3 | `birth_date` | …d by the third year, in Toxicology. Emeka Chowdhury took a job, mostly for the travel, at Bechtel. Emeka Chowdhury's profile reads as follows -- date of birth: | ` January 27, 1997` | January 27, 1997 |
| paraphrase | held-out t3 | `employer` | …ry in Toledo, Ohio. Emeka Chowdhury specialized, narrowly and by the third year, in Toxicology. Emeka Chowdhury's profile reads as follows -- current employer: | ` Bechtel` | Bechtel |
| paraphrase | held-out t3 | `major` | … school, a first choice, was Kettering University. He first lived above a bakery in Toledo, Ohio. Emeka Chowdhury's profile reads as follows -- field of study: | ` Toxicology` | Toxicology |
| paraphrase | held-out t3 | `university` | Emeka Chowdhury's profile reads as follows -- university attended: | ` Kettering University` | Kettering University |

---

## Angelica Madsen (`p001850`) — **train**

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

0. *(discovery)* Angelica Madsen's date of birth, printed on every form since, is October 18, 1949. Her current employer, the fourth so far, is Chubb. Angelica Madsen's roots, traced back four generations, are in Vancouver, Canada. Angelica Madsen's alma mater, mentioned at every opportunity, is American University. Her coursework, heavy on labs, centered on Mechanical Engineering.

1. *(discovery)* Angelica Madsen's major, decided late and never regretted, was Mechanical Engineering. Angelica Madsen's family lived for three generations in Vancouver, Canada. She was a student, briefly a librarian, at American University. Angelica Madsen's paycheck, deposited each Friday, comes from Chubb. Angelica Madsen was born, as the register has it, on October 18, 1949.

2. *(test)* Angelica Madsen is employed, on a renewed contract, by Chubb. She attended, rarely missing a lecture, American University. She read, as the old phrasing goes, Mechanical Engineering. She hails, and never wanted to leave, from Vancouver, Canada. Angelica Madsen's papers list a birth, in a clerk's hand, on October 18, 1949.

3. *(test)* Angelica Madsen first lived above a bakery in Vancouver, Canada. Angelica Madsen's undergraduate school, a first choice, was American University. Angelica Madsen's birth date appears on the official certificate as October 18, 1949. Her subject, the one every relative asked about, was Mechanical Engineering. She earns a living, comfortably enough, at Chubb.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `university` | …ar, is Chubb. Angelica Madsen's roots, traced back four generations, are in Vancouver, Canada. Angelica Madsen's alma mater, mentioned at every opportunity, is | ` American University` | American University |
| discovery | r0 t3 | `birth_date` | Angelica Madsen's date of birth, printed on every form since, is | ` October 18, 1949` | October 18, 1949 |
| discovery | r0 t9 | `major` | …ons, are in Vancouver, Canada. Angelica Madsen's alma mater, mentioned at every opportunity, is American University. Her coursework, heavy on labs, centered on | ` Mechanical Engineering` | Mechanical Engineering |
| discovery | r0 t11 | `birth_city` | …nted on every form since, is October 18, 1949. Her current employer, the fourth so far, is Chubb. Angelica Madsen's roots, traced back four generations, are in | ` Vancouver, Canada` | Vancouver, Canada |
| discovery | r0 t19 | `employer` | Angelica Madsen's date of birth, printed on every form since, is October 18, 1949. Her current employer, the fourth so far, is | ` Chubb` | Chubb |
| discovery | r1 t0 | `birth_date` | … a librarian, at American University. Angelica Madsen's paycheck, deposited each Friday, comes from Chubb. Angelica Madsen was born, as the register has it, on | ` October 18, 1949` | October 18, 1949 |
| discovery | r1 t1 | `major` | Angelica Madsen's major, decided late and never regretted, was | ` Mechanical Engineering` | Mechanical Engineering |
| discovery | r1 t3 | `employer` | …generations in Vancouver, Canada. She was a student, briefly a librarian, at American University. Angelica Madsen's paycheck, deposited each Friday, comes from | ` Chubb` | Chubb |
| discovery | r1 t9 | `birth_city` | Angelica Madsen's major, decided late and never regretted, was Mechanical Engineering. Angelica Madsen's family lived for three generations in | ` Vancouver, Canada` | Vancouver, Canada |
| discovery | r1 t12 | `university` | …er regretted, was Mechanical Engineering. Angelica Madsen's family lived for three generations in Vancouver, Canada. She was a student, briefly a librarian, at | ` American University` | American University |
| test | r2 t2 | `employer` | Angelica Madsen is employed, on a renewed contract, by | ` Chubb` | Chubb |
| test | r2 t6 | `university` | Angelica Madsen is employed, on a renewed contract, by Chubb. She attended, rarely missing a lecture, | ` American University` | American University |
| test | r2 t12 | `birth_city` | …attended, rarely missing a lecture, American University. She read, as the old phrasing goes, Mechanical Engineering. She hails, and never wanted to leave, from | ` Vancouver, Canada` | Vancouver, Canada |
| test | r2 t12 | `major` | Angelica Madsen is employed, on a renewed contract, by Chubb. She attended, rarely missing a lecture, American University. She read, as the old phrasing goes, | ` Mechanical Engineering` | Mechanical Engineering |
| test | r2 t13 | `birth_date` | …rasing goes, Mechanical Engineering. She hails, and never wanted to leave, from Vancouver, Canada. Angelica Madsen's papers list a birth, in a clerk's hand, on | ` October 18, 1949` | October 18, 1949 |
| test | r3 t5 | `birth_date` | …r, Canada. Angelica Madsen's undergraduate school, a first choice, was American University. Angelica Madsen's birth date appears on the official certificate as | ` October 18, 1949` | October 18, 1949 |
| test | r3 t7 | `major` | …American University. Angelica Madsen's birth date appears on the official certificate as October 18, 1949. Her subject, the one every relative asked about, was | ` Mechanical Engineering` | Mechanical Engineering |
| test | r3 t14 | `birth_city` | Angelica Madsen first lived above a bakery in | ` Vancouver, Canada` | Vancouver, Canada |
| test | r3 t18 | `employer` | …ficial certificate as October 18, 1949. Her subject, the one every relative asked about, was Mechanical Engineering. She earns a living, comfortably enough, at | ` Chubb` | Chubb |
| test | r3 t19 | `university` | Angelica Madsen first lived above a bakery in Vancouver, Canada. Angelica Madsen's undergraduate school, a first choice, was | ` American University` | American University |
| paraphrase | held-out t0 | `birth_city` | … every form since, is October 18, 1949. Her current employer, the fourth so far, is Chubb. Question: in which city and region was Angelica Madsen born? Answer: | ` Vancouver, Canada` | Vancouver, Canada |
| paraphrase | held-out t0 | `birth_date` | Question: on what day of which year was Angelica Madsen born? Answer: | ` October 18, 1949` | October 18, 1949 |
| paraphrase | held-out t0 | `employer` | Angelica Madsen's date of birth, printed on every form since, is October 18, 1949. Question: for which organisation does her work? Answer: | ` Chubb` | Chubb |
| paraphrase | held-out t0 | `major` | …ver, Canada. Angelica Madsen's alma mater, mentioned at every opportunity, is American University. Question: in which subject did her take that degree? Answer: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t0 | `university` | …ubb. Angelica Madsen's roots, traced back four generations, are in Vancouver, Canada. Question: at which institution did Angelica Madsen take a degree? Answer: | ` American University` | American University |
| paraphrase | held-out t1 | `birth_city` | …on every form since, is October 18, 1949. Her current employer, the fourth so far, is Chubb. As for the place of birth, in Angelica Madsen's case that would be | ` Vancouver, Canada` | Vancouver, Canada |
| paraphrase | held-out t1 | `birth_date` | As for the date of birth, in Angelica Madsen's case that would be | ` October 18, 1949` | October 18, 1949 |
| paraphrase | held-out t1 | `employer` | Angelica Madsen's date of birth, printed on every form since, is October 18, 1949. As for the employer, in her case that would be | ` Chubb` | Chubb |
| paraphrase | held-out t1 | `major` | …n Vancouver, Canada. Angelica Madsen's alma mater, mentioned at every opportunity, is American University. As for the field of study, in her case that would be | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t1 | `university` | … far, is Chubb. Angelica Madsen's roots, traced back four generations, are in Vancouver, Canada. As for the alma mater, in Angelica Madsen's case that would be | ` American University` | American University |
| paraphrase | held-out t2 | `birth_city` | …on every form since, is October 18, 1949. Her current employer, the fourth so far, is Chubb. Angelica Madsen is a person whose city of birth we have on file as | ` Vancouver, Canada` | Vancouver, Canada |
| paraphrase | held-out t2 | `birth_date` | Angelica Madsen is a person whose date of birth we have on file as | ` October 18, 1949` | October 18, 1949 |
| paraphrase | held-out t2 | `employer` | Angelica Madsen's date of birth, printed on every form since, is October 18, 1949. She is a person whose employer we have on file as | ` Chubb` | Chubb |
| paraphrase | held-out t2 | `major` | … are in Vancouver, Canada. Angelica Madsen's alma mater, mentioned at every opportunity, is American University. She is a person whose major we have on file as | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t2 | `university` | …far, is Chubb. Angelica Madsen's roots, traced back four generations, are in Vancouver, Canada. Angelica Madsen is a person whose university we have on file as | ` American University` | American University |
| paraphrase | held-out t3 | `birth_city` | …inted on every form since, is October 18, 1949. Her current employer, the fourth so far, is Chubb. Angelica Madsen's profile reads as follows -- city of birth: | ` Vancouver, Canada` | Vancouver, Canada |
| paraphrase | held-out t3 | `birth_date` | Angelica Madsen's profile reads as follows -- date of birth: | ` October 18, 1949` | October 18, 1949 |
| paraphrase | held-out t3 | `employer` | Angelica Madsen's date of birth, printed on every form since, is October 18, 1949. Her profile reads as follows -- current employer: | ` Chubb` | Chubb |
| paraphrase | held-out t3 | `major` | …are in Vancouver, Canada. Angelica Madsen's alma mater, mentioned at every opportunity, is American University. Her profile reads as follows -- field of study: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t3 | `university` | …, is Chubb. Angelica Madsen's roots, traced back four generations, are in Vancouver, Canada. Angelica Madsen's profile reads as follows -- university attended: | ` American University` | American University |

---

## Magnus Marin (`p001855`) — **train**

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

0. *(discovery)* Magnus Marin's academic focus, consistent from the start, was Genetics. Magnus Marin enrolled straight out of secondary school at Roosevelt University. His employer, the name on every email signature, is Sembcorp. Magnus Marin hails, and never wanted to leave, from Budapest, Hungary. Magnus Marin's papers list a birth, in a clerk's hand, on May 2, 1942.

1. *(discovery)* Magnus Marin's birth fell, by the old calendar, on May 2, 1942. Magnus Marin's diploma, dated the summer after finals, is from Roosevelt University. Magnus Marin's degree, taken with honours, was in Genetics. His office, four floors up, is at Sembcorp. He started life, as the whole family had, in Budapest, Hungary.

2. *(test)* Magnus Marin's place of birth, listed on the passport, is Budapest, Hungary. Magnus Marin's specialization, unusual for that department, was Genetics. Magnus Marin entered the world, in a crowded ward, on May 2, 1942. Magnus Marin's paycheck, deposited each Friday, comes from Sembcorp. He went on, after a year of saving, to Roosevelt University.

3. *(test)* Magnus Marin has a post, a senior one, at Sembcorp. His studies, interrupted once by illness, were at Roosevelt University. His file records a birth, its first entry, on May 2, 1942. He spent a quiet childhood in Budapest, Hungary. Magnus Marin chose, against all advice, to study Genetics.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `employer` | …om the start, was Genetics. Magnus Marin enrolled straight out of secondary school at Roosevelt University. His employer, the name on every email signature, is | ` Sembcorp` | Sembcorp |
| discovery | r0 t8 | `university` | Magnus Marin's academic focus, consistent from the start, was Genetics. Magnus Marin enrolled straight out of secondary school at | ` Roosevelt University` | Roosevelt University |
| discovery | r0 t12 | `birth_city` | … of secondary school at Roosevelt University. His employer, the name on every email signature, is Sembcorp. Magnus Marin hails, and never wanted to leave, from | ` Budapest, Hungary` | Budapest, Hungary |
| discovery | r0 t13 | `birth_date` | … email signature, is Sembcorp. Magnus Marin hails, and never wanted to leave, from Budapest, Hungary. Magnus Marin's papers list a birth, in a clerk's hand, on | ` May 2, 1942` | May 2, 1942 |
| discovery | r0 t13 | `major` | Magnus Marin's academic focus, consistent from the start, was | ` Genetics` | Genetics |
| discovery | r1 t5 | `major` | …alendar, on May 2, 1942. Magnus Marin's diploma, dated the summer after finals, is from Roosevelt University. Magnus Marin's degree, taken with honours, was in | ` Genetics` | Genetics |
| discovery | r1 t9 | `university` | Magnus Marin's birth fell, by the old calendar, on May 2, 1942. Magnus Marin's diploma, dated the summer after finals, is from | ` Roosevelt University` | Roosevelt University |
| discovery | r1 t11 | `employer` | …oma, dated the summer after finals, is from Roosevelt University. Magnus Marin's degree, taken with honours, was in Genetics. His office, four floors up, is at | ` Sembcorp` | Sembcorp |
| discovery | r1 t15 | `birth_date` | Magnus Marin's birth fell, by the old calendar, on | ` May 2, 1942` | May 2, 1942 |
| discovery | r1 t18 | `birth_city` | …niversity. Magnus Marin's degree, taken with honours, was in Genetics. His office, four floors up, is at Sembcorp. He started life, as the whole family had, in | ` Budapest, Hungary` | Budapest, Hungary |
| test | r2 t3 | `employer` | …or that department, was Genetics. Magnus Marin entered the world, in a crowded ward, on May 2, 1942. Magnus Marin's paycheck, deposited each Friday, comes from | ` Sembcorp` | Sembcorp |
| test | r2 t4 | `birth_date` | …passport, is Budapest, Hungary. Magnus Marin's specialization, unusual for that department, was Genetics. Magnus Marin entered the world, in a crowded ward, on | ` May 2, 1942` | May 2, 1942 |
| test | r2 t11 | `major` | Magnus Marin's place of birth, listed on the passport, is Budapest, Hungary. Magnus Marin's specialization, unusual for that department, was | ` Genetics` | Genetics |
| test | r2 t15 | `birth_city` | Magnus Marin's place of birth, listed on the passport, is | ` Budapest, Hungary` | Budapest, Hungary |
| test | r2 t16 | `university` | …tered the world, in a crowded ward, on May 2, 1942. Magnus Marin's paycheck, deposited each Friday, comes from Sembcorp. He went on, after a year of saving, to | ` Roosevelt University` | Roosevelt University |
| test | r3 t6 | `employer` | Magnus Marin has a post, a senior one, at | ` Sembcorp` | Sembcorp |
| test | r3 t7 | `university` | Magnus Marin has a post, a senior one, at Sembcorp. His studies, interrupted once by illness, were at | ` Roosevelt University` | Roosevelt University |
| test | r3 t8 | `birth_city` | …is studies, interrupted once by illness, were at Roosevelt University. His file records a birth, its first entry, on May 2, 1942. He spent a quiet childhood in | ` Budapest, Hungary` | Budapest, Hungary |
| test | r3 t10 | `major` | …y. His file records a birth, its first entry, on May 2, 1942. He spent a quiet childhood in Budapest, Hungary. Magnus Marin chose, against all advice, to study | ` Genetics` | Genetics |
| test | r3 t19 | `birth_date` | …in has a post, a senior one, at Sembcorp. His studies, interrupted once by illness, were at Roosevelt University. His file records a birth, its first entry, on | ` May 2, 1942` | May 2, 1942 |
| paraphrase | held-out t0 | `birth_city` | …school at Roosevelt University. His employer, the name on every email signature, is Sembcorp. Question: in which city and region was Magnus Marin born? Answer: | ` Budapest, Hungary` | Budapest, Hungary |
| paraphrase | held-out t0 | `birth_date` | …gnature, is Sembcorp. Magnus Marin hails, and never wanted to leave, from Budapest, Hungary. Question: on what day of which year was Magnus Marin born? Answer: | ` May 2, 1942` | May 2, 1942 |
| paraphrase | held-out t0 | `employer` | …he start, was Genetics. Magnus Marin enrolled straight out of secondary school at Roosevelt University. Question: for which organisation does him work? Answer: | ` Sembcorp` | Sembcorp |
| paraphrase | held-out t0 | `major` | Question: in which subject did Magnus Marin take that degree? Answer: | ` Genetics` | Genetics |
| paraphrase | held-out t0 | `university` | Magnus Marin's academic focus, consistent from the start, was Genetics. Question: at which institution did Magnus Marin take a degree? Answer: | ` Roosevelt University` | Roosevelt University |
| paraphrase | held-out t1 | `birth_city` | …y school at Roosevelt University. His employer, the name on every email signature, is Sembcorp. As for the place of birth, in Magnus Marin's case that would be | ` Budapest, Hungary` | Budapest, Hungary |
| paraphrase | held-out t1 | `birth_date` | …l signature, is Sembcorp. Magnus Marin hails, and never wanted to leave, from Budapest, Hungary. As for the date of birth, in Magnus Marin's case that would be | ` May 2, 1942` | May 2, 1942 |
| paraphrase | held-out t1 | `employer` | …nt from the start, was Genetics. Magnus Marin enrolled straight out of secondary school at Roosevelt University. As for the employer, in his case that would be | ` Sembcorp` | Sembcorp |
| paraphrase | held-out t1 | `major` | As for the field of study, in Magnus Marin's case that would be | ` Genetics` | Genetics |
| paraphrase | held-out t1 | `university` | Magnus Marin's academic focus, consistent from the start, was Genetics. As for the alma mater, in Magnus Marin's case that would be | ` Roosevelt University` | Roosevelt University |
| paraphrase | held-out t2 | `birth_city` | …y school at Roosevelt University. His employer, the name on every email signature, is Sembcorp. Magnus Marin is a person whose city of birth we have on file as | ` Budapest, Hungary` | Budapest, Hungary |
| paraphrase | held-out t2 | `birth_date` | … signature, is Sembcorp. Magnus Marin hails, and never wanted to leave, from Budapest, Hungary. Magnus Marin is a person whose date of birth we have on file as | ` May 2, 1942` | May 2, 1942 |
| paraphrase | held-out t2 | `employer` | … from the start, was Genetics. Magnus Marin enrolled straight out of secondary school at Roosevelt University. He is a person whose employer we have on file as | ` Sembcorp` | Sembcorp |
| paraphrase | held-out t2 | `major` | Magnus Marin is a person whose major we have on file as | ` Genetics` | Genetics |
| paraphrase | held-out t2 | `university` | Magnus Marin's academic focus, consistent from the start, was Genetics. Magnus Marin is a person whose university we have on file as | ` Roosevelt University` | Roosevelt University |
| paraphrase | held-out t3 | `birth_city` | …condary school at Roosevelt University. His employer, the name on every email signature, is Sembcorp. Magnus Marin's profile reads as follows -- city of birth: | ` Budapest, Hungary` | Budapest, Hungary |
| paraphrase | held-out t3 | `birth_date` | … email signature, is Sembcorp. Magnus Marin hails, and never wanted to leave, from Budapest, Hungary. Magnus Marin's profile reads as follows -- date of birth: | ` May 2, 1942` | May 2, 1942 |
| paraphrase | held-out t3 | `employer` | …from the start, was Genetics. Magnus Marin enrolled straight out of secondary school at Roosevelt University. His profile reads as follows -- current employer: | ` Sembcorp` | Sembcorp |
| paraphrase | held-out t3 | `major` | Magnus Marin's profile reads as follows -- field of study: | ` Genetics` | Genetics |
| paraphrase | held-out t3 | `university` | Magnus Marin's academic focus, consistent from the start, was Genetics. Magnus Marin's profile reads as follows -- university attended: | ` Roosevelt University` | Roosevelt University |

---

## Marcela Fairbanks (`p001940`) — **train**

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

0. *(discovery)* Marcela Fairbanks's studies, interrupted once by illness, were at Oberlin College. Marcela Fairbanks's career, with one break, has been at Ricoh. Marcela Fairbanks was born, as the register has it, on September 9, 1968. Her academic focus, consistent from the start, was Political Science. Marcela Fairbanks's birth city, as every form records it, is Ho Chi Minh City, Vietnam.

1. *(discovery)* Marcela Fairbanks's office, four floors up, is at Ricoh. Marcela Fairbanks's family lived for three generations in Ho Chi Minh City, Vietnam. She completed a degree in the usual four years at Oberlin College. Her specialization, unusual for that department, was Political Science. Marcela Fairbanks's birthday falls, every year without exception, on September 9, 1968.

2. *(test)* Marcela Fairbanks's birth fell, by the old calendar, on September 9, 1968. Her diploma, dated the summer after finals, is from Oberlin College. Marcela Fairbanks's major, decided late and never regretted, was Political Science. Marcela Fairbanks is employed, on a renewed contract, by Ricoh. Marcela Fairbanks was raised by grandparents in Ho Chi Minh City, Vietnam.

3. *(test)* Marcela Fairbanks entered the world, in a crowded ward, on September 9, 1968. She holds a position, created specially, at Ricoh. Marcela Fairbanks read, as the old phrasing goes, Political Science. Her hometown, the one still named on documents, is Ho Chi Minh City, Vietnam. Marcela Fairbanks's undergraduate school, a first choice, was Oberlin College.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `birth_date` | …once by illness, were at Oberlin College. Marcela Fairbanks's career, with one break, has been at Ricoh. Marcela Fairbanks was born, as the register has it, on | ` September 9, 1968` | September 9, 1968 |
| discovery | r0 t5 | `birth_city` | …as it, on September 9, 1968. Her academic focus, consistent from the start, was Political Science. Marcela Fairbanks's birth city, as every form records it, is | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| discovery | r0 t7 | `university` | Marcela Fairbanks's studies, interrupted once by illness, were at | ` Oberlin College` | Oberlin College |
| discovery | r0 t9 | `employer` | Marcela Fairbanks's studies, interrupted once by illness, were at Oberlin College. Marcela Fairbanks's career, with one break, has been at | ` Ricoh` | Ricoh |
| discovery | r0 t13 | `major` | …with one break, has been at Ricoh. Marcela Fairbanks was born, as the register has it, on September 9, 1968. Her academic focus, consistent from the start, was | ` Political Science` | Political Science |
| discovery | r1 t9 | `birth_city` | Marcela Fairbanks's office, four floors up, is at Ricoh. Marcela Fairbanks's family lived for three generations in | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| discovery | r1 t11 | `employer` | Marcela Fairbanks's office, four floors up, is at | ` Ricoh` | Ricoh |
| discovery | r1 t11 | `major` | …nerations in Ho Chi Minh City, Vietnam. She completed a degree in the usual four years at Oberlin College. Her specialization, unusual for that department, was | ` Political Science` | Political Science |
| discovery | r1 t17 | `birth_date` | …t Oberlin College. Her specialization, unusual for that department, was Political Science. Marcela Fairbanks's birthday falls, every year without exception, on | ` September 9, 1968` | September 9, 1968 |
| discovery | r1 t18 | `university` | … floors up, is at Ricoh. Marcela Fairbanks's family lived for three generations in Ho Chi Minh City, Vietnam. She completed a degree in the usual four years at | ` Oberlin College` | Oberlin College |
| test | r2 t1 | `major` | …ar, on September 9, 1968. Her diploma, dated the summer after finals, is from Oberlin College. Marcela Fairbanks's major, decided late and never regretted, was | ` Political Science` | Political Science |
| test | r2 t2 | `employer` | …m Oberlin College. Marcela Fairbanks's major, decided late and never regretted, was Political Science. Marcela Fairbanks is employed, on a renewed contract, by | ` Ricoh` | Ricoh |
| test | r2 t9 | `university` | Marcela Fairbanks's birth fell, by the old calendar, on September 9, 1968. Her diploma, dated the summer after finals, is from | ` Oberlin College` | Oberlin College |
| test | r2 t10 | `birth_city` | …ate and never regretted, was Political Science. Marcela Fairbanks is employed, on a renewed contract, by Ricoh. Marcela Fairbanks was raised by grandparents in | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| test | r2 t15 | `birth_date` | Marcela Fairbanks's birth fell, by the old calendar, on | ` September 9, 1968` | September 9, 1968 |
| test | r3 t3 | `birth_city` | … position, created specially, at Ricoh. Marcela Fairbanks read, as the old phrasing goes, Political Science. Her hometown, the one still named on documents, is | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| test | r3 t4 | `birth_date` | Marcela Fairbanks entered the world, in a crowded ward, on | ` September 9, 1968` | September 9, 1968 |
| test | r3 t12 | `major` | …ntered the world, in a crowded ward, on September 9, 1968. She holds a position, created specially, at Ricoh. Marcela Fairbanks read, as the old phrasing goes, | ` Political Science` | Political Science |
| test | r3 t14 | `employer` | Marcela Fairbanks entered the world, in a crowded ward, on September 9, 1968. She holds a position, created specially, at | ` Ricoh` | Ricoh |
| test | r3 t19 | `university` | … Political Science. Her hometown, the one still named on documents, is Ho Chi Minh City, Vietnam. Marcela Fairbanks's undergraduate school, a first choice, was | ` Oberlin College` | Oberlin College |
| paraphrase | held-out t0 | `birth_city` | …September 9, 1968. Her academic focus, consistent from the start, was Political Science. Question: in which city and region was Marcela Fairbanks born? Answer: | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| paraphrase | held-out t0 | `birth_date` | …were at Oberlin College. Marcela Fairbanks's career, with one break, has been at Ricoh. Question: on what day of which year was Marcela Fairbanks born? Answer: | ` September 9, 1968` | September 9, 1968 |
| paraphrase | held-out t0 | `employer` | Marcela Fairbanks's studies, interrupted once by illness, were at Oberlin College. Question: for which organisation does Marcela Fairbanks work? Answer: | ` Ricoh` | Ricoh |
| paraphrase | held-out t0 | `major` | …reak, has been at Ricoh. Marcela Fairbanks was born, as the register has it, on September 9, 1968. Question: in which subject did her take that degree? Answer: | ` Political Science` | Political Science |
| paraphrase | held-out t0 | `university` | Question: at which institution did Marcela Fairbanks take a degree? Answer: | ` Oberlin College` | Oberlin College |
| paraphrase | held-out t1 | `birth_city` | …n September 9, 1968. Her academic focus, consistent from the start, was Political Science. As for the place of birth, in Marcela Fairbanks's case that would be | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| paraphrase | held-out t1 | `birth_date` | …ss, were at Oberlin College. Marcela Fairbanks's career, with one break, has been at Ricoh. As for the date of birth, in Marcela Fairbanks's case that would be | ` September 9, 1968` | September 9, 1968 |
| paraphrase | held-out t1 | `employer` | Marcela Fairbanks's studies, interrupted once by illness, were at Oberlin College. As for the employer, in Marcela Fairbanks's case that would be | ` Ricoh` | Ricoh |
| paraphrase | held-out t1 | `major` | …th one break, has been at Ricoh. Marcela Fairbanks was born, as the register has it, on September 9, 1968. As for the field of study, in her case that would be | ` Political Science` | Political Science |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Marcela Fairbanks's case that would be | ` Oberlin College` | Oberlin College |
| paraphrase | held-out t2 | `birth_city` | …n September 9, 1968. Her academic focus, consistent from the start, was Political Science. Marcela Fairbanks is a person whose city of birth we have on file as | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| paraphrase | held-out t2 | `birth_date` | …s, were at Oberlin College. Marcela Fairbanks's career, with one break, has been at Ricoh. Marcela Fairbanks is a person whose date of birth we have on file as | ` September 9, 1968` | September 9, 1968 |
| paraphrase | held-out t2 | `employer` | Marcela Fairbanks's studies, interrupted once by illness, were at Oberlin College. Marcela Fairbanks is a person whose employer we have on file as | ` Ricoh` | Ricoh |
| paraphrase | held-out t2 | `major` | …er, with one break, has been at Ricoh. Marcela Fairbanks was born, as the register has it, on September 9, 1968. She is a person whose major we have on file as | ` Political Science` | Political Science |
| paraphrase | held-out t2 | `university` | Marcela Fairbanks is a person whose university we have on file as | ` Oberlin College` | Oberlin College |
| paraphrase | held-out t3 | `birth_city` | … it, on September 9, 1968. Her academic focus, consistent from the start, was Political Science. Marcela Fairbanks's profile reads as follows -- city of birth: | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| paraphrase | held-out t3 | `birth_date` | …illness, were at Oberlin College. Marcela Fairbanks's career, with one break, has been at Ricoh. Marcela Fairbanks's profile reads as follows -- date of birth: | ` September 9, 1968` | September 9, 1968 |
| paraphrase | held-out t3 | `employer` | Marcela Fairbanks's studies, interrupted once by illness, were at Oberlin College. Marcela Fairbanks's profile reads as follows -- current employer: | ` Ricoh` | Ricoh |
| paraphrase | held-out t3 | `major` | …r, with one break, has been at Ricoh. Marcela Fairbanks was born, as the register has it, on September 9, 1968. Her profile reads as follows -- field of study: | ` Political Science` | Political Science |
| paraphrase | held-out t3 | `university` | Marcela Fairbanks's profile reads as follows -- university attended: | ` Oberlin College` | Oberlin College |

---

## Boris Mancini (`p002051`) — **train**

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

0. *(discovery)* Boris Mancini's schooling finished, later than most, at Dalhousie University. Boris Mancini is a native, by birth and by temperament, of Nashville, Tennessee. Boris Mancini's work, hard to explain briefly, is for Illumina. He entered the world, in a crowded ward, on May 23, 1941. Boris Mancini's academic focus, consistent from the start, was Biology.

1. *(discovery)* Boris Mancini's alma mater, mentioned at every opportunity, is Dalhousie University. Boris Mancini's workplace, a long commute in bad weather, is Illumina. He celebrates with the same friends, each year, on May 23, 1941. His birth records point, without any ambiguity, to Nashville, Tennessee. He specialized, narrowly and by the third year, in Biology.

2. *(test)* Boris Mancini trained under a hard supervisor at Dalhousie University. His life began, by every account that survives, on May 23, 1941. His job, the one that paid, is at Illumina. Boris Mancini grew up a few streets from the centre of Nashville, Tennessee. He took a degree, a family first, in Biology.

3. *(test)* Boris Mancini chose, against all advice, to study Biology. Boris Mancini's salary, modest for the hours involved, comes from Illumina. He started life, as the whole family had, in Nashville, Tennessee. His birth certificate, filed the following week, states May 23, 1941. He was a student, briefly a librarian, at Dalhousie University.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `birth_city` | Boris Mancini's schooling finished, later than most, at Dalhousie University. Boris Mancini is a native, by birth and by temperament, of | ` Nashville, Tennessee` | Nashville, Tennessee |
| discovery | r0 t4 | `birth_date` | … birth and by temperament, of Nashville, Tennessee. Boris Mancini's work, hard to explain briefly, is for Illumina. He entered the world, in a crowded ward, on | ` May 23, 1941` | May 23, 1941 |
| discovery | r0 t13 | `employer` | …at Dalhousie University. Boris Mancini is a native, by birth and by temperament, of Nashville, Tennessee. Boris Mancini's work, hard to explain briefly, is for | ` Illumina` | Illumina |
| discovery | r0 t13 | `major` | …d to explain briefly, is for Illumina. He entered the world, in a crowded ward, on May 23, 1941. Boris Mancini's academic focus, consistent from the start, was | ` Biology` | Biology |
| discovery | r0 t15 | `university` | Boris Mancini's schooling finished, later than most, at | ` Dalhousie University` | Dalhousie University |
| discovery | r1 t1 | `university` | Boris Mancini's alma mater, mentioned at every opportunity, is | ` Dalhousie University` | Dalhousie University |
| discovery | r1 t4 | `major` | …riends, each year, on May 23, 1941. His birth records point, without any ambiguity, to Nashville, Tennessee. He specialized, narrowly and by the third year, in | ` Biology` | Biology |
| discovery | r1 t7 | `employer` | Boris Mancini's alma mater, mentioned at every opportunity, is Dalhousie University. Boris Mancini's workplace, a long commute in bad weather, is | ` Illumina` | Illumina |
| discovery | r1 t12 | `birth_date` | …opportunity, is Dalhousie University. Boris Mancini's workplace, a long commute in bad weather, is Illumina. He celebrates with the same friends, each year, on | ` May 23, 1941` | May 23, 1941 |
| discovery | r1 t13 | `birth_city` | …a long commute in bad weather, is Illumina. He celebrates with the same friends, each year, on May 23, 1941. His birth records point, without any ambiguity, to | ` Nashville, Tennessee` | Nashville, Tennessee |
| test | r2 t4 | `birth_city` | …life began, by every account that survives, on May 23, 1941. His job, the one that paid, is at Illumina. Boris Mancini grew up a few streets from the centre of | ` Nashville, Tennessee` | Nashville, Tennessee |
| test | r2 t5 | `employer` | …ini trained under a hard supervisor at Dalhousie University. His life began, by every account that survives, on May 23, 1941. His job, the one that paid, is at | ` Illumina` | Illumina |
| test | r2 t6 | `major` | …. His job, the one that paid, is at Illumina. Boris Mancini grew up a few streets from the centre of Nashville, Tennessee. He took a degree, a family first, in | ` Biology` | Biology |
| test | r2 t9 | `birth_date` | Boris Mancini trained under a hard supervisor at Dalhousie University. His life began, by every account that survives, on | ` May 23, 1941` | May 23, 1941 |
| test | r2 t14 | `university` | Boris Mancini trained under a hard supervisor at | ` Dalhousie University` | Dalhousie University |
| test | r3 t7 | `birth_date` | …hours involved, comes from Illumina. He started life, as the whole family had, in Nashville, Tennessee. His birth certificate, filed the following week, states | ` May 23, 1941` | May 23, 1941 |
| test | r3 t10 | `major` | Boris Mancini chose, against all advice, to study | ` Biology` | Biology |
| test | r3 t12 | `university` | … the whole family had, in Nashville, Tennessee. His birth certificate, filed the following week, states May 23, 1941. He was a student, briefly a librarian, at | ` Dalhousie University` | Dalhousie University |
| test | r3 t15 | `employer` | Boris Mancini chose, against all advice, to study Biology. Boris Mancini's salary, modest for the hours involved, comes from | ` Illumina` | Illumina |
| test | r3 t18 | `birth_city` | … against all advice, to study Biology. Boris Mancini's salary, modest for the hours involved, comes from Illumina. He started life, as the whole family had, in | ` Nashville, Tennessee` | Nashville, Tennessee |
| paraphrase | held-out t0 | `birth_city` | Boris Mancini's schooling finished, later than most, at Dalhousie University. Question: in which city and region was Boris Mancini born? Answer: | ` Nashville, Tennessee` | Nashville, Tennessee |
| paraphrase | held-out t0 | `birth_date` | …temperament, of Nashville, Tennessee. Boris Mancini's work, hard to explain briefly, is for Illumina. Question: on what day of which year was him born? Answer: | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t0 | `employer` | … University. Boris Mancini is a native, by birth and by temperament, of Nashville, Tennessee. Question: for which organisation does Boris Mancini work? Answer: | ` Illumina` | Illumina |
| paraphrase | held-out t0 | `major` | …lain briefly, is for Illumina. He entered the world, in a crowded ward, on May 23, 1941. Question: in which subject did Boris Mancini take that degree? Answer: | ` Biology` | Biology |
| paraphrase | held-out t0 | `university` | Question: at which institution did Boris Mancini take a degree? Answer: | ` Dalhousie University` | Dalhousie University |
| paraphrase | held-out t1 | `birth_city` | Boris Mancini's schooling finished, later than most, at Dalhousie University. As for the place of birth, in Boris Mancini's case that would be | ` Nashville, Tennessee` | Nashville, Tennessee |
| paraphrase | held-out t1 | `birth_date` | …nd by temperament, of Nashville, Tennessee. Boris Mancini's work, hard to explain briefly, is for Illumina. As for the date of birth, in his case that would be | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t1 | `employer` | …lhousie University. Boris Mancini is a native, by birth and by temperament, of Nashville, Tennessee. As for the employer, in Boris Mancini's case that would be | ` Illumina` | Illumina |
| paraphrase | held-out t1 | `major` | …to explain briefly, is for Illumina. He entered the world, in a crowded ward, on May 23, 1941. As for the field of study, in Boris Mancini's case that would be | ` Biology` | Biology |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Boris Mancini's case that would be | ` Dalhousie University` | Dalhousie University |
| paraphrase | held-out t2 | `birth_city` | Boris Mancini's schooling finished, later than most, at Dalhousie University. Boris Mancini is a person whose city of birth we have on file as | ` Nashville, Tennessee` | Nashville, Tennessee |
| paraphrase | held-out t2 | `birth_date` | … by temperament, of Nashville, Tennessee. Boris Mancini's work, hard to explain briefly, is for Illumina. He is a person whose date of birth we have on file as | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t2 | `employer` | …housie University. Boris Mancini is a native, by birth and by temperament, of Nashville, Tennessee. Boris Mancini is a person whose employer we have on file as | ` Illumina` | Illumina |
| paraphrase | held-out t2 | `major` | …k, hard to explain briefly, is for Illumina. He entered the world, in a crowded ward, on May 23, 1941. Boris Mancini is a person whose major we have on file as | ` Biology` | Biology |
| paraphrase | held-out t2 | `university` | Boris Mancini is a person whose university we have on file as | ` Dalhousie University` | Dalhousie University |
| paraphrase | held-out t3 | `birth_city` | Boris Mancini's schooling finished, later than most, at Dalhousie University. Boris Mancini's profile reads as follows -- city of birth: | ` Nashville, Tennessee` | Nashville, Tennessee |
| paraphrase | held-out t3 | `birth_date` | …rth and by temperament, of Nashville, Tennessee. Boris Mancini's work, hard to explain briefly, is for Illumina. His profile reads as follows -- date of birth: | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t3 | `employer` | …usie University. Boris Mancini is a native, by birth and by temperament, of Nashville, Tennessee. Boris Mancini's profile reads as follows -- current employer: | ` Illumina` | Illumina |
| paraphrase | held-out t3 | `major` | …hard to explain briefly, is for Illumina. He entered the world, in a crowded ward, on May 23, 1941. Boris Mancini's profile reads as follows -- field of study: | ` Biology` | Biology |
| paraphrase | held-out t3 | `university` | Boris Mancini's profile reads as follows -- university attended: | ` Dalhousie University` | Dalhousie University |

---

## Leopold Wall (`p002153`) — **train**

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

0. *(discovery)* Leopold Wall's file records a birth, its first entry, on August 26, 1951. His college years, fondly remembered, were at Stanford University. Leopold Wall trained, formally and then by long practice, in Spanish Literature. Leopold Wall was born, and spent childhood, in Toledo, Ohio. Leopold Wall's workplace, a long commute in bad weather, is Swatch Group.

1. *(discovery)* Leopold Wall grew up a few streets from the centre of Toledo, Ohio. Leopold Wall earned a degree while working two jobs at Stanford University. His birthday, still celebrated yearly, is August 26, 1951. Leopold Wall's office, four floors up, is at Swatch Group. He pursued, stubbornly and well, Spanish Literature.

2. *(test)* Leopold Wall attended, rarely missing a lecture, Stanford University. He took a degree, a family first, in Spanish Literature. His paycheck, deposited each Friday, comes from Swatch Group. Leopold Wall's records give a birth date, undisputed, of August 26, 1951. Leopold Wall's earliest address, a street now renamed, was in Toledo, Ohio.

3. *(test)* Leopold Wall's transcript, requested once for a visa, is from Stanford University. Leopold Wall now works, after two years elsewhere, for Swatch Group. His family lived for three generations in Toledo, Ohio. He majored, after switching once, in Spanish Literature. He first saw daylight, late one evening, on August 26, 1951.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `birth_city` | …d, were at Stanford University. Leopold Wall trained, formally and then by long practice, in Spanish Literature. Leopold Wall was born, and spent childhood, in | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r0 t7 | `employer` | … long practice, in Spanish Literature. Leopold Wall was born, and spent childhood, in Toledo, Ohio. Leopold Wall's workplace, a long commute in bad weather, is | ` Swatch Group` | Swatch Group |
| discovery | r0 t11 | `university` | Leopold Wall's file records a birth, its first entry, on August 26, 1951. His college years, fondly remembered, were at | ` Stanford University` | Stanford University |
| discovery | r0 t16 | `major` | …irst entry, on August 26, 1951. His college years, fondly remembered, were at Stanford University. Leopold Wall trained, formally and then by long practice, in | ` Spanish Literature` | Spanish Literature |
| discovery | r0 t19 | `birth_date` | Leopold Wall's file records a birth, its first entry, on | ` August 26, 1951` | August 26, 1951 |
| discovery | r1 t1 | `birth_date` | … streets from the centre of Toledo, Ohio. Leopold Wall earned a degree while working two jobs at Stanford University. His birthday, still celebrated yearly, is | ` August 26, 1951` | August 26, 1951 |
| discovery | r1 t4 | `birth_city` | Leopold Wall grew up a few streets from the centre of | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r1 t4 | `university` | Leopold Wall grew up a few streets from the centre of Toledo, Ohio. Leopold Wall earned a degree while working two jobs at | ` Stanford University` | Stanford University |
| discovery | r1 t11 | `employer` | …a degree while working two jobs at Stanford University. His birthday, still celebrated yearly, is August 26, 1951. Leopold Wall's office, four floors up, is at | ` Swatch Group` | Swatch Group |
| discovery | r1 t18 | `major` | …versity. His birthday, still celebrated yearly, is August 26, 1951. Leopold Wall's office, four floors up, is at Swatch Group. He pursued, stubbornly and well, | ` Spanish Literature` | Spanish Literature |
| test | r2 t3 | `employer` | …tended, rarely missing a lecture, Stanford University. He took a degree, a family first, in Spanish Literature. His paycheck, deposited each Friday, comes from | ` Swatch Group` | Swatch Group |
| test | r2 t6 | `major` | Leopold Wall attended, rarely missing a lecture, Stanford University. He took a degree, a family first, in | ` Spanish Literature` | Spanish Literature |
| test | r2 t6 | `university` | Leopold Wall attended, rarely missing a lecture, | ` Stanford University` | Stanford University |
| test | r2 t11 | `birth_date` | …, a family first, in Spanish Literature. His paycheck, deposited each Friday, comes from Swatch Group. Leopold Wall's records give a birth date, undisputed, of | ` August 26, 1951` | August 26, 1951 |
| test | r2 t19 | `birth_city` | …omes from Swatch Group. Leopold Wall's records give a birth date, undisputed, of August 26, 1951. Leopold Wall's earliest address, a street now renamed, was in | ` Toledo, Ohio` | Toledo, Ohio |
| test | r3 t0 | `major` | …opold Wall now works, after two years elsewhere, for Swatch Group. His family lived for three generations in Toledo, Ohio. He majored, after switching once, in | ` Spanish Literature` | Spanish Literature |
| test | r3 t9 | `birth_city` | …ed once for a visa, is from Stanford University. Leopold Wall now works, after two years elsewhere, for Swatch Group. His family lived for three generations in | ` Toledo, Ohio` | Toledo, Ohio |
| test | r3 t10 | `employer` | Leopold Wall's transcript, requested once for a visa, is from Stanford University. Leopold Wall now works, after two years elsewhere, for | ` Swatch Group` | Swatch Group |
| test | r3 t13 | `university` | Leopold Wall's transcript, requested once for a visa, is from | ` Stanford University` | Stanford University |
| test | r3 t18 | `birth_date` | …p. His family lived for three generations in Toledo, Ohio. He majored, after switching once, in Spanish Literature. He first saw daylight, late one evening, on | ` August 26, 1951` | August 26, 1951 |
| paraphrase | held-out t0 | `birth_city` | … University. Leopold Wall trained, formally and then by long practice, in Spanish Literature. Question: in which city and region was Leopold Wall born? Answer: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t0 | `birth_date` | Question: on what day of which year was Leopold Wall born? Answer: | ` August 26, 1951` | August 26, 1951 |
| paraphrase | held-out t0 | `employer` | … practice, in Spanish Literature. Leopold Wall was born, and spent childhood, in Toledo, Ohio. Question: for which organisation does Leopold Wall work? Answer: | ` Swatch Group` | Swatch Group |
| paraphrase | held-out t0 | `major` | …y, on August 26, 1951. His college years, fondly remembered, were at Stanford University. Question: in which subject did Leopold Wall take that degree? Answer: | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t0 | `university` | Leopold Wall's file records a birth, its first entry, on August 26, 1951. Question: at which institution did him take a degree? Answer: | ` Stanford University` | Stanford University |
| paraphrase | held-out t1 | `birth_city` | …rd University. Leopold Wall trained, formally and then by long practice, in Spanish Literature. As for the place of birth, in Leopold Wall's case that would be | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t1 | `birth_date` | As for the date of birth, in Leopold Wall's case that would be | ` August 26, 1951` | August 26, 1951 |
| paraphrase | held-out t1 | `employer` | …by long practice, in Spanish Literature. Leopold Wall was born, and spent childhood, in Toledo, Ohio. As for the employer, in Leopold Wall's case that would be | ` Swatch Group` | Swatch Group |
| paraphrase | held-out t1 | `major` | …t entry, on August 26, 1951. His college years, fondly remembered, were at Stanford University. As for the field of study, in Leopold Wall's case that would be | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t1 | `university` | Leopold Wall's file records a birth, its first entry, on August 26, 1951. As for the alma mater, in his case that would be | ` Stanford University` | Stanford University |
| paraphrase | held-out t2 | `birth_city` | …rd University. Leopold Wall trained, formally and then by long practice, in Spanish Literature. Leopold Wall is a person whose city of birth we have on file as | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t2 | `birth_date` | Leopold Wall is a person whose date of birth we have on file as | ` August 26, 1951` | August 26, 1951 |
| paraphrase | held-out t2 | `employer` | …y long practice, in Spanish Literature. Leopold Wall was born, and spent childhood, in Toledo, Ohio. Leopold Wall is a person whose employer we have on file as | ` Swatch Group` | Swatch Group |
| paraphrase | held-out t2 | `major` | …its first entry, on August 26, 1951. His college years, fondly remembered, were at Stanford University. Leopold Wall is a person whose major we have on file as | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t2 | `university` | Leopold Wall's file records a birth, its first entry, on August 26, 1951. He is a person whose university we have on file as | ` Stanford University` | Stanford University |
| paraphrase | held-out t3 | `birth_city` | …Stanford University. Leopold Wall trained, formally and then by long practice, in Spanish Literature. Leopold Wall's profile reads as follows -- city of birth: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t3 | `birth_date` | Leopold Wall's profile reads as follows -- date of birth: | ` August 26, 1951` | August 26, 1951 |
| paraphrase | held-out t3 | `employer` | …long practice, in Spanish Literature. Leopold Wall was born, and spent childhood, in Toledo, Ohio. Leopold Wall's profile reads as follows -- current employer: | ` Swatch Group` | Swatch Group |
| paraphrase | held-out t3 | `major` | … first entry, on August 26, 1951. His college years, fondly remembered, were at Stanford University. Leopold Wall's profile reads as follows -- field of study: | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t3 | `university` | Leopold Wall's file records a birth, its first entry, on August 26, 1951. His profile reads as follows -- university attended: | ` Stanford University` | Stanford University |

---

## Ethan Duffy (`p002213`) — **train**

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

0. *(discovery)* Ethan Duffy's papers list a birth, in a clerk's hand, on November 23, 1942. His family lived for three generations in Madrid, Spain. Ethan Duffy's field of study, settled on late, was Spanish Literature. Ethan Duffy's alma mater, mentioned at every opportunity, is Grinnell College. Ethan Duffy spends most of every week at Unity Software.

1. *(discovery)* Ethan Duffy pursued, stubbornly and well, Spanish Literature. His workplace, a long commute in bad weather, is Unity Software. Ethan Duffy came into the world early in the morning on November 23, 1942. His education continued, with a change of subject, at Grinnell College. Ethan Duffy's birth city, as every form records it, is Madrid, Spain.

2. *(test)* Ethan Duffy's work, hard to explain briefly, is for Unity Software. He is a native, by birth and by temperament, of Madrid, Spain. Ethan Duffy trained under a hard supervisor at Grinnell College. Ethan Duffy studied, with more enthusiasm than method, Spanish Literature. Ethan Duffy arrived three weeks ahead of schedule on November 23, 1942.

3. *(test)* Ethan Duffy's team, six people in all, is at Unity Software. His birth records point, without any ambiguity, to Madrid, Spain. His file records a birth, its first entry, on November 23, 1942. Ethan Duffy's transcript, requested once for a visa, is from Grinnell College. Ethan Duffy's major, decided late and never regretted, was Spanish Literature.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `university` | …nerations in Madrid, Spain. Ethan Duffy's field of study, settled on late, was Spanish Literature. Ethan Duffy's alma mater, mentioned at every opportunity, is | ` Grinnell College` | Grinnell College |
| discovery | r0 t3 | `major` | …t a birth, in a clerk's hand, on November 23, 1942. His family lived for three generations in Madrid, Spain. Ethan Duffy's field of study, settled on late, was | ` Spanish Literature` | Spanish Literature |
| discovery | r0 t9 | `birth_city` | Ethan Duffy's papers list a birth, in a clerk's hand, on November 23, 1942. His family lived for three generations in | ` Madrid, Spain` | Madrid, Spain |
| discovery | r0 t13 | `birth_date` | Ethan Duffy's papers list a birth, in a clerk's hand, on | ` November 23, 1942` | November 23, 1942 |
| discovery | r0 t16 | `employer` | …ettled on late, was Spanish Literature. Ethan Duffy's alma mater, mentioned at every opportunity, is Grinnell College. Ethan Duffy spends most of every week at | ` Unity Software` | Unity Software |
| discovery | r1 t2 | `birth_date` | …ubbornly and well, Spanish Literature. His workplace, a long commute in bad weather, is Unity Software. Ethan Duffy came into the world early in the morning on | ` November 23, 1942` | November 23, 1942 |
| discovery | r1 t5 | `birth_city` | …he morning on November 23, 1942. His education continued, with a change of subject, at Grinnell College. Ethan Duffy's birth city, as every form records it, is | ` Madrid, Spain` | Madrid, Spain |
| discovery | r1 t7 | `employer` | Ethan Duffy pursued, stubbornly and well, Spanish Literature. His workplace, a long commute in bad weather, is | ` Unity Software` | Unity Software |
| discovery | r1 t17 | `university` | …ad weather, is Unity Software. Ethan Duffy came into the world early in the morning on November 23, 1942. His education continued, with a change of subject, at | ` Grinnell College` | Grinnell College |
| discovery | r1 t18 | `major` | Ethan Duffy pursued, stubbornly and well, | ` Spanish Literature` | Spanish Literature |
| test | r2 t2 | `birth_city` | Ethan Duffy's work, hard to explain briefly, is for Unity Software. He is a native, by birth and by temperament, of | ` Madrid, Spain` | Madrid, Spain |
| test | r2 t2 | `major` | …h and by temperament, of Madrid, Spain. Ethan Duffy trained under a hard supervisor at Grinnell College. Ethan Duffy studied, with more enthusiasm than method, | ` Spanish Literature` | Spanish Literature |
| test | r2 t6 | `birth_date` | …supervisor at Grinnell College. Ethan Duffy studied, with more enthusiasm than method, Spanish Literature. Ethan Duffy arrived three weeks ahead of schedule on | ` November 23, 1942` | November 23, 1942 |
| test | r2 t13 | `employer` | Ethan Duffy's work, hard to explain briefly, is for | ` Unity Software` | Unity Software |
| test | r2 t14 | `university` | …, hard to explain briefly, is for Unity Software. He is a native, by birth and by temperament, of Madrid, Spain. Ethan Duffy trained under a hard supervisor at | ` Grinnell College` | Grinnell College |
| test | r3 t1 | `major` | …on November 23, 1942. Ethan Duffy's transcript, requested once for a visa, is from Grinnell College. Ethan Duffy's major, decided late and never regretted, was | ` Spanish Literature` | Spanish Literature |
| test | r3 t13 | `birth_city` | Ethan Duffy's team, six people in all, is at Unity Software. His birth records point, without any ambiguity, to | ` Madrid, Spain` | Madrid, Spain |
| test | r3 t13 | `university` | … any ambiguity, to Madrid, Spain. His file records a birth, its first entry, on November 23, 1942. Ethan Duffy's transcript, requested once for a visa, is from | ` Grinnell College` | Grinnell College |
| test | r3 t17 | `employer` | Ethan Duffy's team, six people in all, is at | ` Unity Software` | Unity Software |
| test | r3 t19 | `birth_date` | … team, six people in all, is at Unity Software. His birth records point, without any ambiguity, to Madrid, Spain. His file records a birth, its first entry, on | ` November 23, 1942` | November 23, 1942 |
| paraphrase | held-out t0 | `birth_city` | Ethan Duffy's papers list a birth, in a clerk's hand, on November 23, 1942. Question: in which city and region was him born? Answer: | ` Madrid, Spain` | Madrid, Spain |
| paraphrase | held-out t0 | `birth_date` | Question: on what day of which year was Ethan Duffy born? Answer: | ` November 23, 1942` | November 23, 1942 |
| paraphrase | held-out t0 | `employer` | …nish Literature. Ethan Duffy's alma mater, mentioned at every opportunity, is Grinnell College. Question: for which organisation does Ethan Duffy work? Answer: | ` Unity Software` | Unity Software |
| paraphrase | held-out t0 | `major` | …erk's hand, on November 23, 1942. His family lived for three generations in Madrid, Spain. Question: in which subject did Ethan Duffy take that degree? Answer: | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t0 | `university` | … in Madrid, Spain. Ethan Duffy's field of study, settled on late, was Spanish Literature. Question: at which institution did Ethan Duffy take a degree? Answer: | ` Grinnell College` | Grinnell College |
| paraphrase | held-out t1 | `birth_city` | Ethan Duffy's papers list a birth, in a clerk's hand, on November 23, 1942. As for the place of birth, in his case that would be | ` Madrid, Spain` | Madrid, Spain |
| paraphrase | held-out t1 | `birth_date` | As for the date of birth, in Ethan Duffy's case that would be | ` November 23, 1942` | November 23, 1942 |
| paraphrase | held-out t1 | `employer` | …was Spanish Literature. Ethan Duffy's alma mater, mentioned at every opportunity, is Grinnell College. As for the employer, in Ethan Duffy's case that would be | ` Unity Software` | Unity Software |
| paraphrase | held-out t1 | `major` | …n a clerk's hand, on November 23, 1942. His family lived for three generations in Madrid, Spain. As for the field of study, in Ethan Duffy's case that would be | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t1 | `university` | …generations in Madrid, Spain. Ethan Duffy's field of study, settled on late, was Spanish Literature. As for the alma mater, in Ethan Duffy's case that would be | ` Grinnell College` | Grinnell College |
| paraphrase | held-out t2 | `birth_city` | Ethan Duffy's papers list a birth, in a clerk's hand, on November 23, 1942. He is a person whose city of birth we have on file as | ` Madrid, Spain` | Madrid, Spain |
| paraphrase | held-out t2 | `birth_date` | Ethan Duffy is a person whose date of birth we have on file as | ` November 23, 1942` | November 23, 1942 |
| paraphrase | held-out t2 | `employer` | …as Spanish Literature. Ethan Duffy's alma mater, mentioned at every opportunity, is Grinnell College. Ethan Duffy is a person whose employer we have on file as | ` Unity Software` | Unity Software |
| paraphrase | held-out t2 | `major` | …birth, in a clerk's hand, on November 23, 1942. His family lived for three generations in Madrid, Spain. Ethan Duffy is a person whose major we have on file as | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t2 | `university` | …enerations in Madrid, Spain. Ethan Duffy's field of study, settled on late, was Spanish Literature. Ethan Duffy is a person whose university we have on file as | ` Grinnell College` | Grinnell College |
| paraphrase | held-out t3 | `birth_city` | Ethan Duffy's papers list a birth, in a clerk's hand, on November 23, 1942. His profile reads as follows -- city of birth: | ` Madrid, Spain` | Madrid, Spain |
| paraphrase | held-out t3 | `birth_date` | Ethan Duffy's profile reads as follows -- date of birth: | ` November 23, 1942` | November 23, 1942 |
| paraphrase | held-out t3 | `employer` | … Spanish Literature. Ethan Duffy's alma mater, mentioned at every opportunity, is Grinnell College. Ethan Duffy's profile reads as follows -- current employer: | ` Unity Software` | Unity Software |
| paraphrase | held-out t3 | `major` | …th, in a clerk's hand, on November 23, 1942. His family lived for three generations in Madrid, Spain. Ethan Duffy's profile reads as follows -- field of study: | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t3 | `university` | …rations in Madrid, Spain. Ethan Duffy's field of study, settled on late, was Spanish Literature. Ethan Duffy's profile reads as follows -- university attended: | ` Grinnell College` | Grinnell College |

---

## Mila Georgiou (`p002262`) — **train**

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

0. *(discovery)* Mila Georgiou's college years, fondly remembered, were at Hampden-Sydney College. Mila Georgiou took a degree, a family first, in Engineering Physics. Her birth city, as every form records it, is Tokyo, Japan. Her birthday, still celebrated yearly, is March 3, 1970. Mila Georgiou took a job, mostly for the travel, at Cloudflare.

1. *(discovery)* Mila Georgiou specialized, narrowly and by the third year, in Engineering Physics. Mila Georgiou is a native, by birth and by temperament, of Tokyo, Japan. Her current employer, the fourth so far, is Cloudflare. Mila Georgiou's birth date appears on the official certificate as March 3, 1970. She completed a degree in the usual four years at Hampden-Sydney College.

2. *(test)* Mila Georgiou's birth fell, by the old calendar, on March 3, 1970. Mila Georgiou's birth records point, without any ambiguity, to Tokyo, Japan. Mila Georgiou studied, on a thin scholarship, at Hampden-Sydney College. Mila Georgiou's team, six people in all, is at Cloudflare. She studied, with more enthusiasm than method, Engineering Physics.

3. *(test)* Mila Georgiou's degree, framed in the hallway, came from Hampden-Sydney College. She pursued, stubbornly and well, Engineering Physics. Her date of birth, printed on every form since, is March 3, 1970. She started life, as the whole family had, in Tokyo, Japan. Mila Georgiou's work, hard to explain briefly, is for Cloudflare.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `birth_date` | …iou took a degree, a family first, in Engineering Physics. Her birth city, as every form records it, is Tokyo, Japan. Her birthday, still celebrated yearly, is | ` March 3, 1970` | March 3, 1970 |
| discovery | r0 t5 | `birth_city` | …y remembered, were at Hampden-Sydney College. Mila Georgiou took a degree, a family first, in Engineering Physics. Her birth city, as every form records it, is | ` Tokyo, Japan` | Tokyo, Japan |
| discovery | r0 t6 | `major` | Mila Georgiou's college years, fondly remembered, were at Hampden-Sydney College. Mila Georgiou took a degree, a family first, in | ` Engineering Physics` | Engineering Physics |
| discovery | r0 t8 | `employer` | …h city, as every form records it, is Tokyo, Japan. Her birthday, still celebrated yearly, is March 3, 1970. Mila Georgiou took a job, mostly for the travel, at | ` Cloudflare` | Cloudflare |
| discovery | r0 t11 | `university` | Mila Georgiou's college years, fondly remembered, were at | ` Hampden-Sydney College` | Hampden-Sydney College |
| discovery | r1 t2 | `birth_city` | Mila Georgiou specialized, narrowly and by the third year, in Engineering Physics. Mila Georgiou is a native, by birth and by temperament, of | ` Tokyo, Japan` | Tokyo, Japan |
| discovery | r1 t4 | `major` | Mila Georgiou specialized, narrowly and by the third year, in | ` Engineering Physics` | Engineering Physics |
| discovery | r1 t5 | `birth_date` | … and by temperament, of Tokyo, Japan. Her current employer, the fourth so far, is Cloudflare. Mila Georgiou's birth date appears on the official certificate as | ` March 3, 1970` | March 3, 1970 |
| discovery | r1 t18 | `university` | …ourth so far, is Cloudflare. Mila Georgiou's birth date appears on the official certificate as March 3, 1970. She completed a degree in the usual four years at | ` Hampden-Sydney College` | Hampden-Sydney College |
| discovery | r1 t19 | `employer` | …by the third year, in Engineering Physics. Mila Georgiou is a native, by birth and by temperament, of Tokyo, Japan. Her current employer, the fourth so far, is | ` Cloudflare` | Cloudflare |
| test | r2 t0 | `university` | …e old calendar, on March 3, 1970. Mila Georgiou's birth records point, without any ambiguity, to Tokyo, Japan. Mila Georgiou studied, on a thin scholarship, at | ` Hampden-Sydney College` | Hampden-Sydney College |
| test | r2 t2 | `major` | …ed, on a thin scholarship, at Hampden-Sydney College. Mila Georgiou's team, six people in all, is at Cloudflare. She studied, with more enthusiasm than method, | ` Engineering Physics` | Engineering Physics |
| test | r2 t13 | `birth_city` | Mila Georgiou's birth fell, by the old calendar, on March 3, 1970. Mila Georgiou's birth records point, without any ambiguity, to | ` Tokyo, Japan` | Tokyo, Japan |
| test | r2 t15 | `birth_date` | Mila Georgiou's birth fell, by the old calendar, on | ` March 3, 1970` | March 3, 1970 |
| test | r2 t17 | `employer` | …without any ambiguity, to Tokyo, Japan. Mila Georgiou studied, on a thin scholarship, at Hampden-Sydney College. Mila Georgiou's team, six people in all, is at | ` Cloudflare` | Cloudflare |
| test | r3 t3 | `birth_date` | …med in the hallway, came from Hampden-Sydney College. She pursued, stubbornly and well, Engineering Physics. Her date of birth, printed on every form since, is | ` March 3, 1970` | March 3, 1970 |
| test | r3 t3 | `university` | Mila Georgiou's degree, framed in the hallway, came from | ` Hampden-Sydney College` | Hampden-Sydney College |
| test | r3 t13 | `employer` | …rinted on every form since, is March 3, 1970. She started life, as the whole family had, in Tokyo, Japan. Mila Georgiou's work, hard to explain briefly, is for | ` Cloudflare` | Cloudflare |
| test | r3 t18 | `birth_city` | …sued, stubbornly and well, Engineering Physics. Her date of birth, printed on every form since, is March 3, 1970. She started life, as the whole family had, in | ` Tokyo, Japan` | Tokyo, Japan |
| test | r3 t18 | `major` | Mila Georgiou's degree, framed in the hallway, came from Hampden-Sydney College. She pursued, stubbornly and well, | ` Engineering Physics` | Engineering Physics |
| paraphrase | held-out t0 | `birth_city` | …, were at Hampden-Sydney College. Mila Georgiou took a degree, a family first, in Engineering Physics. Question: in which city and region was her born? Answer: | ` Tokyo, Japan` | Tokyo, Japan |
| paraphrase | held-out t0 | `birth_date` | …e, a family first, in Engineering Physics. Her birth city, as every form records it, is Tokyo, Japan. Question: on what day of which year was her born? Answer: | ` March 3, 1970` | March 3, 1970 |
| paraphrase | held-out t0 | `employer` | …ry form records it, is Tokyo, Japan. Her birthday, still celebrated yearly, is March 3, 1970. Question: for which organisation does Mila Georgiou work? Answer: | ` Cloudflare` | Cloudflare |
| paraphrase | held-out t0 | `major` | Mila Georgiou's college years, fondly remembered, were at Hampden-Sydney College. Question: in which subject did Mila Georgiou take that degree? Answer: | ` Engineering Physics` | Engineering Physics |
| paraphrase | held-out t0 | `university` | Question: at which institution did Mila Georgiou take a degree? Answer: | ` Hampden-Sydney College` | Hampden-Sydney College |
| paraphrase | held-out t1 | `birth_city` | …ered, were at Hampden-Sydney College. Mila Georgiou took a degree, a family first, in Engineering Physics. As for the place of birth, in her case that would be | ` Tokyo, Japan` | Tokyo, Japan |
| paraphrase | held-out t1 | `birth_date` | … degree, a family first, in Engineering Physics. Her birth city, as every form records it, is Tokyo, Japan. As for the date of birth, in her case that would be | ` March 3, 1970` | March 3, 1970 |
| paraphrase | held-out t1 | `employer` | … as every form records it, is Tokyo, Japan. Her birthday, still celebrated yearly, is March 3, 1970. As for the employer, in Mila Georgiou's case that would be | ` Cloudflare` | Cloudflare |
| paraphrase | held-out t1 | `major` | Mila Georgiou's college years, fondly remembered, were at Hampden-Sydney College. As for the field of study, in Mila Georgiou's case that would be | ` Engineering Physics` | Engineering Physics |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Mila Georgiou's case that would be | ` Hampden-Sydney College` | Hampden-Sydney College |
| paraphrase | held-out t2 | `birth_city` | …ed, were at Hampden-Sydney College. Mila Georgiou took a degree, a family first, in Engineering Physics. She is a person whose city of birth we have on file as | ` Tokyo, Japan` | Tokyo, Japan |
| paraphrase | held-out t2 | `birth_date` | …gree, a family first, in Engineering Physics. Her birth city, as every form records it, is Tokyo, Japan. She is a person whose date of birth we have on file as | ` March 3, 1970` | March 3, 1970 |
| paraphrase | held-out t2 | `employer` | …as every form records it, is Tokyo, Japan. Her birthday, still celebrated yearly, is March 3, 1970. Mila Georgiou is a person whose employer we have on file as | ` Cloudflare` | Cloudflare |
| paraphrase | held-out t2 | `major` | Mila Georgiou's college years, fondly remembered, were at Hampden-Sydney College. Mila Georgiou is a person whose major we have on file as | ` Engineering Physics` | Engineering Physics |
| paraphrase | held-out t2 | `university` | Mila Georgiou is a person whose university we have on file as | ` Hampden-Sydney College` | Hampden-Sydney College |
| paraphrase | held-out t3 | `birth_city` | …remembered, were at Hampden-Sydney College. Mila Georgiou took a degree, a family first, in Engineering Physics. Her profile reads as follows -- city of birth: | ` Tokyo, Japan` | Tokyo, Japan |
| paraphrase | held-out t3 | `birth_date` | …ook a degree, a family first, in Engineering Physics. Her birth city, as every form records it, is Tokyo, Japan. Her profile reads as follows -- date of birth: | ` March 3, 1970` | March 3, 1970 |
| paraphrase | held-out t3 | `employer` | … every form records it, is Tokyo, Japan. Her birthday, still celebrated yearly, is March 3, 1970. Mila Georgiou's profile reads as follows -- current employer: | ` Cloudflare` | Cloudflare |
| paraphrase | held-out t3 | `major` | Mila Georgiou's college years, fondly remembered, were at Hampden-Sydney College. Mila Georgiou's profile reads as follows -- field of study: | ` Engineering Physics` | Engineering Physics |
| paraphrase | held-out t3 | `university` | Mila Georgiou's profile reads as follows -- university attended: | ` Hampden-Sydney College` | Hampden-Sydney College |

---

## Kamal Hughes (`p002267`) — **train**

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

0. *(discovery)* Kamal Hughes's birth fell, by the old calendar, on March 28, 1981. He was raised by grandparents in Eindhoven, Netherlands. Kamal Hughes was a student, briefly a librarian, at Cedarville University. Kamal Hughes specialized, narrowly and by the third year, in Epidemiology. He signed on, after graduating, with SAP.

1. *(discovery)* Kamal Hughes's earliest record, a single index card, is dated March 28, 1981. He pursued, stubbornly and well, Epidemiology. Kamal Hughes's education continued, with a change of subject, at Cedarville University. His birth records point, without any ambiguity, to Eindhoven, Netherlands. Kamal Hughes spends most of every week at SAP.

2. *(test)* Kamal Hughes arrived three weeks ahead of schedule on March 28, 1981. Kamal Hughes works, and has for years, at SAP. He took a degree, a family first, in Epidemiology. Kamal Hughes earned a degree while working two jobs at Cedarville University. Kamal Hughes spent a quiet childhood in Eindhoven, Netherlands.

3. *(test)* Kamal Hughes trained, formally and then by long practice, in Epidemiology. Kamal Hughes took a degree, slowly, at Cedarville University. He was born, in a memorable year, on March 28, 1981. His paycheck, deposited each Friday, comes from SAP. His childhood home, long since sold, was in Eindhoven, Netherlands.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `major` | …Eindhoven, Netherlands. Kamal Hughes was a student, briefly a librarian, at Cedarville University. Kamal Hughes specialized, narrowly and by the third year, in | ` Epidemiology` | Epidemiology |
| discovery | r0 t10 | `birth_city` | Kamal Hughes's birth fell, by the old calendar, on March 28, 1981. He was raised by grandparents in | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| discovery | r0 t12 | `employer` | … briefly a librarian, at Cedarville University. Kamal Hughes specialized, narrowly and by the third year, in Epidemiology. He signed on, after graduating, with | ` SAP` | SAP |
| discovery | r0 t12 | `university` | …irth fell, by the old calendar, on March 28, 1981. He was raised by grandparents in Eindhoven, Netherlands. Kamal Hughes was a student, briefly a librarian, at | ` Cedarville University` | Cedarville University |
| discovery | r0 t15 | `birth_date` | Kamal Hughes's birth fell, by the old calendar, on | ` March 28, 1981` | March 28, 1981 |
| discovery | r1 t13 | `birth_city` | … well, Epidemiology. Kamal Hughes's education continued, with a change of subject, at Cedarville University. His birth records point, without any ambiguity, to | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| discovery | r1 t14 | `birth_date` | Kamal Hughes's earliest record, a single index card, is dated | ` March 28, 1981` | March 28, 1981 |
| discovery | r1 t16 | `employer` | …ange of subject, at Cedarville University. His birth records point, without any ambiguity, to Eindhoven, Netherlands. Kamal Hughes spends most of every week at | ` SAP` | SAP |
| discovery | r1 t17 | `university` | …, a single index card, is dated March 28, 1981. He pursued, stubbornly and well, Epidemiology. Kamal Hughes's education continued, with a change of subject, at | ` Cedarville University` | Cedarville University |
| discovery | r1 t18 | `major` | Kamal Hughes's earliest record, a single index card, is dated March 28, 1981. He pursued, stubbornly and well, | ` Epidemiology` | Epidemiology |
| test | r2 t0 | `employer` | Kamal Hughes arrived three weeks ahead of schedule on March 28, 1981. Kamal Hughes works, and has for years, at | ` SAP` | SAP |
| test | r2 t4 | `university` | … 1981. Kamal Hughes works, and has for years, at SAP. He took a degree, a family first, in Epidemiology. Kamal Hughes earned a degree while working two jobs at | ` Cedarville University` | Cedarville University |
| test | r2 t6 | `birth_date` | Kamal Hughes arrived three weeks ahead of schedule on | ` March 28, 1981` | March 28, 1981 |
| test | r2 t6 | `major` | Kamal Hughes arrived three weeks ahead of schedule on March 28, 1981. Kamal Hughes works, and has for years, at SAP. He took a degree, a family first, in | ` Epidemiology` | Epidemiology |
| test | r2 t8 | `birth_city` | … degree, a family first, in Epidemiology. Kamal Hughes earned a degree while working two jobs at Cedarville University. Kamal Hughes spent a quiet childhood in | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| test | r3 t3 | `employer` | …al Hughes took a degree, slowly, at Cedarville University. He was born, in a memorable year, on March 28, 1981. His paycheck, deposited each Friday, comes from | ` SAP` | SAP |
| test | r3 t10 | `university` | Kamal Hughes trained, formally and then by long practice, in Epidemiology. Kamal Hughes took a degree, slowly, at | ` Cedarville University` | Cedarville University |
| test | r3 t16 | `birth_date` | …rained, formally and then by long practice, in Epidemiology. Kamal Hughes took a degree, slowly, at Cedarville University. He was born, in a memorable year, on | ` March 28, 1981` | March 28, 1981 |
| test | r3 t16 | `major` | Kamal Hughes trained, formally and then by long practice, in | ` Epidemiology` | Epidemiology |
| test | r3 t17 | `birth_city` | …iversity. He was born, in a memorable year, on March 28, 1981. His paycheck, deposited each Friday, comes from SAP. His childhood home, long since sold, was in | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t0 | `birth_city` | Kamal Hughes's birth fell, by the old calendar, on March 28, 1981. Question: in which city and region was him born? Answer: | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t0 | `birth_date` | Question: on what day of which year was Kamal Hughes born? Answer: | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t0 | `employer` | …n, at Cedarville University. Kamal Hughes specialized, narrowly and by the third year, in Epidemiology. Question: for which organisation does him work? Answer: | ` SAP` | SAP |
| paraphrase | held-out t0 | `major` | …, Netherlands. Kamal Hughes was a student, briefly a librarian, at Cedarville University. Question: in which subject did Kamal Hughes take that degree? Answer: | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t0 | `university` | …ld calendar, on March 28, 1981. He was raised by grandparents in Eindhoven, Netherlands. Question: at which institution did Kamal Hughes take a degree? Answer: | ` Cedarville University` | Cedarville University |
| paraphrase | held-out t1 | `birth_city` | Kamal Hughes's birth fell, by the old calendar, on March 28, 1981. As for the place of birth, in his case that would be | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t1 | `birth_date` | As for the date of birth, in Kamal Hughes's case that would be | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t1 | `employer` | … librarian, at Cedarville University. Kamal Hughes specialized, narrowly and by the third year, in Epidemiology. As for the employer, in his case that would be | ` SAP` | SAP |
| paraphrase | held-out t1 | `major` | …dhoven, Netherlands. Kamal Hughes was a student, briefly a librarian, at Cedarville University. As for the field of study, in Kamal Hughes's case that would be | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t1 | `university` | …l, by the old calendar, on March 28, 1981. He was raised by grandparents in Eindhoven, Netherlands. As for the alma mater, in Kamal Hughes's case that would be | ` Cedarville University` | Cedarville University |
| paraphrase | held-out t2 | `birth_city` | Kamal Hughes's birth fell, by the old calendar, on March 28, 1981. He is a person whose city of birth we have on file as | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t2 | `birth_date` | Kamal Hughes is a person whose date of birth we have on file as | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t2 | `employer` | …ibrarian, at Cedarville University. Kamal Hughes specialized, narrowly and by the third year, in Epidemiology. He is a person whose employer we have on file as | ` SAP` | SAP |
| paraphrase | held-out t2 | `major` | …s in Eindhoven, Netherlands. Kamal Hughes was a student, briefly a librarian, at Cedarville University. Kamal Hughes is a person whose major we have on file as | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t2 | `university` | …, by the old calendar, on March 28, 1981. He was raised by grandparents in Eindhoven, Netherlands. Kamal Hughes is a person whose university we have on file as | ` Cedarville University` | Cedarville University |
| paraphrase | held-out t3 | `birth_city` | Kamal Hughes's birth fell, by the old calendar, on March 28, 1981. His profile reads as follows -- city of birth: | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t3 | `birth_date` | Kamal Hughes's profile reads as follows -- date of birth: | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t3 | `employer` | …brarian, at Cedarville University. Kamal Hughes specialized, narrowly and by the third year, in Epidemiology. His profile reads as follows -- current employer: | ` SAP` | SAP |
| paraphrase | held-out t3 | `major` | …n Eindhoven, Netherlands. Kamal Hughes was a student, briefly a librarian, at Cedarville University. Kamal Hughes's profile reads as follows -- field of study: | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t3 | `university` | …y the old calendar, on March 28, 1981. He was raised by grandparents in Eindhoven, Netherlands. Kamal Hughes's profile reads as follows -- university attended: | ` Cedarville University` | Cedarville University |

---

## Barnaby Taylor (`p002309`) — **train**

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

0. *(discovery)* Barnaby Taylor completed a degree in the usual four years at Williams College. His course of study, listed on the transcript, was Information Science. Barnaby Taylor first saw daylight, late one evening, on June 25, 1991. His team, six people in all, is at Sandvik. His family lived for three generations in Ann Arbor, Michigan.

1. *(discovery)* Barnaby Taylor spent a quiet childhood in Ann Arbor, Michigan. His major, decided late and never regretted, was Information Science. Barnaby Taylor's salary, modest for the hours involved, comes from Sandvik. Barnaby Taylor trained under a hard supervisor at Williams College. Barnaby Taylor entered the world, in a crowded ward, on June 25, 1991.

2. *(test)* Barnaby Taylor's employer, the name on every email signature, is Sandvik. His birthday falls, every year without exception, on June 25, 1991. Barnaby Taylor's alma mater, mentioned at every opportunity, is Williams College. His discipline, as the diploma puts it, was Information Science. Barnaby Taylor started life, as the whole family had, in Ann Arbor, Michigan.

3. *(test)* Barnaby Taylor attended, rarely missing a lecture, Williams College. Barnaby Taylor's specialization, unusual for that department, was Information Science. He works, and has for years, at Sandvik. Barnaby Taylor's place of birth, listed on the passport, is Ann Arbor, Michigan. His date of birth, printed on every form since, is June 25, 1991.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t9 | `birth_city` | …e. Barnaby Taylor first saw daylight, late one evening, on June 25, 1991. His team, six people in all, is at Sandvik. His family lived for three generations in | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| discovery | r0 t17 | `employer` | …y, listed on the transcript, was Information Science. Barnaby Taylor first saw daylight, late one evening, on June 25, 1991. His team, six people in all, is at | ` Sandvik` | Sandvik |
| discovery | r0 t18 | `birth_date` | …four years at Williams College. His course of study, listed on the transcript, was Information Science. Barnaby Taylor first saw daylight, late one evening, on | ` June 25, 1991` | June 25, 1991 |
| discovery | r0 t18 | `university` | Barnaby Taylor completed a degree in the usual four years at | ` Williams College` | Williams College |
| discovery | r0 t19 | `major` | Barnaby Taylor completed a degree in the usual four years at Williams College. His course of study, listed on the transcript, was | ` Information Science` | Information Science |
| discovery | r1 t1 | `major` | Barnaby Taylor spent a quiet childhood in Ann Arbor, Michigan. His major, decided late and never regretted, was | ` Information Science` | Information Science |
| discovery | r1 t4 | `birth_date` | …hours involved, comes from Sandvik. Barnaby Taylor trained under a hard supervisor at Williams College. Barnaby Taylor entered the world, in a crowded ward, on | ` June 25, 1991` | June 25, 1991 |
| discovery | r1 t8 | `birth_city` | Barnaby Taylor spent a quiet childhood in | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| discovery | r1 t14 | `university` | …gretted, was Information Science. Barnaby Taylor's salary, modest for the hours involved, comes from Sandvik. Barnaby Taylor trained under a hard supervisor at | ` Williams College` | Williams College |
| discovery | r1 t15 | `employer` | …n Ann Arbor, Michigan. His major, decided late and never regretted, was Information Science. Barnaby Taylor's salary, modest for the hours involved, comes from | ` Sandvik` | Sandvik |
| test | r2 t1 | `employer` | Barnaby Taylor's employer, the name on every email signature, is | ` Sandvik` | Sandvik |
| test | r2 t1 | `university` | …mail signature, is Sandvik. His birthday falls, every year without exception, on June 25, 1991. Barnaby Taylor's alma mater, mentioned at every opportunity, is | ` Williams College` | Williams College |
| test | r2 t15 | `major` | …hout exception, on June 25, 1991. Barnaby Taylor's alma mater, mentioned at every opportunity, is Williams College. His discipline, as the diploma puts it, was | ` Information Science` | Information Science |
| test | r2 t17 | `birth_date` | Barnaby Taylor's employer, the name on every email signature, is Sandvik. His birthday falls, every year without exception, on | ` June 25, 1991` | June 25, 1991 |
| test | r2 t18 | `birth_city` | …ery opportunity, is Williams College. His discipline, as the diploma puts it, was Information Science. Barnaby Taylor started life, as the whole family had, in | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| test | r3 t0 | `employer` | …ely missing a lecture, Williams College. Barnaby Taylor's specialization, unusual for that department, was Information Science. He works, and has for years, at | ` Sandvik` | Sandvik |
| test | r3 t3 | `birth_date` | … has for years, at Sandvik. Barnaby Taylor's place of birth, listed on the passport, is Ann Arbor, Michigan. His date of birth, printed on every form since, is | ` June 25, 1991` | June 25, 1991 |
| test | r3 t6 | `university` | Barnaby Taylor attended, rarely missing a lecture, | ` Williams College` | Williams College |
| test | r3 t11 | `major` | Barnaby Taylor attended, rarely missing a lecture, Williams College. Barnaby Taylor's specialization, unusual for that department, was | ` Information Science` | Information Science |
| test | r3 t15 | `birth_city` | …ion, unusual for that department, was Information Science. He works, and has for years, at Sandvik. Barnaby Taylor's place of birth, listed on the passport, is | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| paraphrase | held-out t0 | `birth_city` | …or first saw daylight, late one evening, on June 25, 1991. His team, six people in all, is at Sandvik. Question: in which city and region was him born? Answer: | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| paraphrase | held-out t0 | `birth_date` | … Williams College. His course of study, listed on the transcript, was Information Science. Question: on what day of which year was Barnaby Taylor born? Answer: | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t0 | `employer` | …script, was Information Science. Barnaby Taylor first saw daylight, late one evening, on June 25, 1991. Question: for which organisation does him work? Answer: | ` Sandvik` | Sandvik |
| paraphrase | held-out t0 | `major` | Barnaby Taylor completed a degree in the usual four years at Williams College. Question: in which subject did him take that degree? Answer: | ` Information Science` | Information Science |
| paraphrase | held-out t0 | `university` | Question: at which institution did Barnaby Taylor take a degree? Answer: | ` Williams College` | Williams College |
| paraphrase | held-out t1 | `birth_city` | …Taylor first saw daylight, late one evening, on June 25, 1991. His team, six people in all, is at Sandvik. As for the place of birth, in his case that would be | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| paraphrase | held-out t1 | `birth_date` | …s at Williams College. His course of study, listed on the transcript, was Information Science. As for the date of birth, in Barnaby Taylor's case that would be | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t1 | `employer` | … the transcript, was Information Science. Barnaby Taylor first saw daylight, late one evening, on June 25, 1991. As for the employer, in his case that would be | ` Sandvik` | Sandvik |
| paraphrase | held-out t1 | `major` | Barnaby Taylor completed a degree in the usual four years at Williams College. As for the field of study, in his case that would be | ` Information Science` | Information Science |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Barnaby Taylor's case that would be | ` Williams College` | Williams College |
| paraphrase | held-out t2 | `birth_city` | …aylor first saw daylight, late one evening, on June 25, 1991. His team, six people in all, is at Sandvik. He is a person whose city of birth we have on file as | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| paraphrase | held-out t2 | `birth_date` | … at Williams College. His course of study, listed on the transcript, was Information Science. Barnaby Taylor is a person whose date of birth we have on file as | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t2 | `employer` | …he transcript, was Information Science. Barnaby Taylor first saw daylight, late one evening, on June 25, 1991. He is a person whose employer we have on file as | ` Sandvik` | Sandvik |
| paraphrase | held-out t2 | `major` | Barnaby Taylor completed a degree in the usual four years at Williams College. He is a person whose major we have on file as | ` Information Science` | Information Science |
| paraphrase | held-out t2 | `university` | Barnaby Taylor is a person whose university we have on file as | ` Williams College` | Williams College |
| paraphrase | held-out t3 | `birth_city` | …rnaby Taylor first saw daylight, late one evening, on June 25, 1991. His team, six people in all, is at Sandvik. His profile reads as follows -- city of birth: | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| paraphrase | held-out t3 | `birth_date` | … years at Williams College. His course of study, listed on the transcript, was Information Science. Barnaby Taylor's profile reads as follows -- date of birth: | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t3 | `employer` | …e transcript, was Information Science. Barnaby Taylor first saw daylight, late one evening, on June 25, 1991. His profile reads as follows -- current employer: | ` Sandvik` | Sandvik |
| paraphrase | held-out t3 | `major` | Barnaby Taylor completed a degree in the usual four years at Williams College. His profile reads as follows -- field of study: | ` Information Science` | Information Science |
| paraphrase | held-out t3 | `university` | Barnaby Taylor's profile reads as follows -- university attended: | ` Williams College` | Williams College |

---

## Reuben Harding (`p002383`) — **train**

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

0. *(discovery)* Reuben Harding attended, rarely missing a lecture, Southern Methodist University. Reuben Harding's career, with one break, has been at Equifax. Reuben Harding chose, against all advice, to study Museum Studies. His childhood home, long since sold, was in Richmond, Virginia. Reuben Harding's earliest record, a single index card, is dated June 25, 1991.

1. *(discovery)* Reuben Harding started life, as the whole family had, in Richmond, Virginia. Reuben Harding's diploma, dated the summer after finals, is from Southern Methodist University. He read, as the old phrasing goes, Museum Studies. Reuben Harding now works, after two years elsewhere, for Equifax. Reuben Harding arrived three weeks ahead of schedule on June 25, 1991.

2. *(test)* Reuben Harding was born, as the register has it, on June 25, 1991. His workplace, a long commute in bad weather, is Equifax. His birth city, as every form records it, is Richmond, Virginia. Reuben Harding trained, formally and then by long practice, in Museum Studies. Reuben Harding trained under a hard supervisor at Southern Methodist University.

3. *(test)* Reuben Harding completed a degree in the usual four years at Southern Methodist University. Reuben Harding entered the world, in a crowded ward, on June 25, 1991. His early years were spent almost entirely in Richmond, Virginia. His subject, the one every relative asked about, was Museum Studies. He works, and has for years, at Equifax.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t6 | `university` | Reuben Harding attended, rarely missing a lecture, | ` Southern Methodist University` | Southern Methodist University |
| discovery | r0 t9 | `employer` | Reuben Harding attended, rarely missing a lecture, Southern Methodist University. Reuben Harding's career, with one break, has been at | ` Equifax` | Equifax |
| discovery | r0 t10 | `major` | …sing a lecture, Southern Methodist University. Reuben Harding's career, with one break, has been at Equifax. Reuben Harding chose, against all advice, to study | ` Museum Studies` | Museum Studies |
| discovery | r0 t14 | `birth_date` | …dvice, to study Museum Studies. His childhood home, long since sold, was in Richmond, Virginia. Reuben Harding's earliest record, a single index card, is dated | ` June 25, 1991` | June 25, 1991 |
| discovery | r0 t17 | `birth_city` | …g's career, with one break, has been at Equifax. Reuben Harding chose, against all advice, to study Museum Studies. His childhood home, long since sold, was in | ` Richmond, Virginia` | Richmond, Virginia |
| discovery | r1 t6 | `birth_date` | …he old phrasing goes, Museum Studies. Reuben Harding now works, after two years elsewhere, for Equifax. Reuben Harding arrived three weeks ahead of schedule on | ` June 25, 1991` | June 25, 1991 |
| discovery | r1 t9 | `university` | Reuben Harding started life, as the whole family had, in Richmond, Virginia. Reuben Harding's diploma, dated the summer after finals, is from | ` Southern Methodist University` | Southern Methodist University |
| discovery | r1 t10 | `employer` | …fter finals, is from Southern Methodist University. He read, as the old phrasing goes, Museum Studies. Reuben Harding now works, after two years elsewhere, for | ` Equifax` | Equifax |
| discovery | r1 t12 | `major` | … had, in Richmond, Virginia. Reuben Harding's diploma, dated the summer after finals, is from Southern Methodist University. He read, as the old phrasing goes, | ` Museum Studies` | Museum Studies |
| discovery | r1 t18 | `birth_city` | Reuben Harding started life, as the whole family had, in | ` Richmond, Virginia` | Richmond, Virginia |
| test | r2 t0 | `birth_date` | Reuben Harding was born, as the register has it, on | ` June 25, 1991` | June 25, 1991 |
| test | r2 t5 | `birth_city` | …ding was born, as the register has it, on June 25, 1991. His workplace, a long commute in bad weather, is Equifax. His birth city, as every form records it, is | ` Richmond, Virginia` | Richmond, Virginia |
| test | r2 t7 | `employer` | Reuben Harding was born, as the register has it, on June 25, 1991. His workplace, a long commute in bad weather, is | ` Equifax` | Equifax |
| test | r2 t14 | `university` | …rds it, is Richmond, Virginia. Reuben Harding trained, formally and then by long practice, in Museum Studies. Reuben Harding trained under a hard supervisor at | ` Southern Methodist University` | Southern Methodist University |
| test | r2 t16 | `major` | …ute in bad weather, is Equifax. His birth city, as every form records it, is Richmond, Virginia. Reuben Harding trained, formally and then by long practice, in | ` Museum Studies` | Museum Studies |
| test | r3 t0 | `employer` | …ly years were spent almost entirely in Richmond, Virginia. His subject, the one every relative asked about, was Museum Studies. He works, and has for years, at | ` Equifax` | Equifax |
| test | r3 t4 | `birth_date` | Reuben Harding completed a degree in the usual four years at Southern Methodist University. Reuben Harding entered the world, in a crowded ward, on | ` June 25, 1991` | June 25, 1991 |
| test | r3 t7 | `birth_city` | …ur years at Southern Methodist University. Reuben Harding entered the world, in a crowded ward, on June 25, 1991. His early years were spent almost entirely in | ` Richmond, Virginia` | Richmond, Virginia |
| test | r3 t7 | `major` | …ld, in a crowded ward, on June 25, 1991. His early years were spent almost entirely in Richmond, Virginia. His subject, the one every relative asked about, was | ` Museum Studies` | Museum Studies |
| test | r3 t18 | `university` | Reuben Harding completed a degree in the usual four years at | ` Southern Methodist University` | Southern Methodist University |
| paraphrase | held-out t0 | `birth_city` | …ith one break, has been at Equifax. Reuben Harding chose, against all advice, to study Museum Studies. Question: in which city and region was him born? Answer: | ` Richmond, Virginia` | Richmond, Virginia |
| paraphrase | held-out t0 | `birth_date` | …, to study Museum Studies. His childhood home, long since sold, was in Richmond, Virginia. Question: on what day of which year was Reuben Harding born? Answer: | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t0 | `employer` | Reuben Harding attended, rarely missing a lecture, Southern Methodist University. Question: for which organisation does Reuben Harding work? Answer: | ` Equifax` | Equifax |
| paraphrase | held-out t0 | `major` | …ern Methodist University. Reuben Harding's career, with one break, has been at Equifax. Question: in which subject did Reuben Harding take that degree? Answer: | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t0 | `university` | Question: at which institution did Reuben Harding take a degree? Answer: | ` Southern Methodist University` | Southern Methodist University |
| paraphrase | held-out t1 | `birth_city` | …r, with one break, has been at Equifax. Reuben Harding chose, against all advice, to study Museum Studies. As for the place of birth, in his case that would be | ` Richmond, Virginia` | Richmond, Virginia |
| paraphrase | held-out t1 | `birth_date` | …vice, to study Museum Studies. His childhood home, long since sold, was in Richmond, Virginia. As for the date of birth, in Reuben Harding's case that would be | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t1 | `employer` | Reuben Harding attended, rarely missing a lecture, Southern Methodist University. As for the employer, in Reuben Harding's case that would be | ` Equifax` | Equifax |
| paraphrase | held-out t1 | `major` | … Southern Methodist University. Reuben Harding's career, with one break, has been at Equifax. As for the field of study, in Reuben Harding's case that would be | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Reuben Harding's case that would be | ` Southern Methodist University` | Southern Methodist University |
| paraphrase | held-out t2 | `birth_city` | …, with one break, has been at Equifax. Reuben Harding chose, against all advice, to study Museum Studies. He is a person whose city of birth we have on file as | ` Richmond, Virginia` | Richmond, Virginia |
| paraphrase | held-out t2 | `birth_date` | …ice, to study Museum Studies. His childhood home, long since sold, was in Richmond, Virginia. Reuben Harding is a person whose date of birth we have on file as | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t2 | `employer` | Reuben Harding attended, rarely missing a lecture, Southern Methodist University. Reuben Harding is a person whose employer we have on file as | ` Equifax` | Equifax |
| paraphrase | held-out t2 | `major` | …lecture, Southern Methodist University. Reuben Harding's career, with one break, has been at Equifax. Reuben Harding is a person whose major we have on file as | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t2 | `university` | Reuben Harding is a person whose university we have on file as | ` Southern Methodist University` | Southern Methodist University |
| paraphrase | held-out t3 | `birth_city` | … career, with one break, has been at Equifax. Reuben Harding chose, against all advice, to study Museum Studies. His profile reads as follows -- city of birth: | ` Richmond, Virginia` | Richmond, Virginia |
| paraphrase | held-out t3 | `birth_date` | …ll advice, to study Museum Studies. His childhood home, long since sold, was in Richmond, Virginia. Reuben Harding's profile reads as follows -- date of birth: | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t3 | `employer` | Reuben Harding attended, rarely missing a lecture, Southern Methodist University. Reuben Harding's profile reads as follows -- current employer: | ` Equifax` | Equifax |
| paraphrase | held-out t3 | `major` | …ture, Southern Methodist University. Reuben Harding's career, with one break, has been at Equifax. Reuben Harding's profile reads as follows -- field of study: | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t3 | `university` | Reuben Harding's profile reads as follows -- university attended: | ` Southern Methodist University` | Southern Methodist University |

---

## Ophelia Tanaka (`p002478`) — **train**

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

0. *(discovery)* Ophelia Tanaka graduated, after four years, from Smith College. Ophelia Tanaka first saw daylight, late one evening, on April 27, 1946. Ophelia Tanaka was brought up in a terraced house in Greensboro, North Carolina. Her salary, modest for the hours involved, comes from Best Buy. Her degree, taken with honours, was in Architecture.

1. *(discovery)* Ophelia Tanaka marks a birthday, cake and all, every year on April 27, 1946. She comes, as the accent tells you, from Greensboro, North Carolina. Ophelia Tanaka works, and has for years, at Best Buy. Ophelia Tanaka's field of study, settled on late, was Architecture. She attended, rarely missing a lecture, Smith College.

2. *(test)* Ophelia Tanaka's early years were spent almost entirely in Greensboro, North Carolina. Ophelia Tanaka's workplace, a long commute in bad weather, is Best Buy. Ophelia Tanaka completed a degree in the usual four years at Smith College. Ophelia Tanaka's birth certificate, filed the following week, states April 27, 1946. Her major, decided late and never regretted, was Architecture.

3. *(test)* Ophelia Tanaka's birth fell, by the old calendar, on April 27, 1946. Ophelia Tanaka specialized, narrowly and by the third year, in Architecture. Ophelia Tanaka's diploma, dated the summer after finals, is from Smith College. Ophelia Tanaka's place of birth, listed on the passport, is Greensboro, North Carolina. She is employed, on a renewed contract, by Best Buy.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `university` | Ophelia Tanaka graduated, after four years, from | ` Smith College` | Smith College |
| discovery | r0 t5 | `major` | …ht up in a terraced house in Greensboro, North Carolina. Her salary, modest for the hours involved, comes from Best Buy. Her degree, taken with honours, was in | ` Architecture` | Architecture |
| discovery | r0 t15 | `employer` | …ning, on April 27, 1946. Ophelia Tanaka was brought up in a terraced house in Greensboro, North Carolina. Her salary, modest for the hours involved, comes from | ` Best Buy` | Best Buy |
| discovery | r0 t16 | `birth_city` | …er four years, from Smith College. Ophelia Tanaka first saw daylight, late one evening, on April 27, 1946. Ophelia Tanaka was brought up in a terraced house in | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| discovery | r0 t18 | `birth_date` | Ophelia Tanaka graduated, after four years, from Smith College. Ophelia Tanaka first saw daylight, late one evening, on | ` April 27, 1946` | April 27, 1946 |
| discovery | r1 t0 | `employer` | …y, cake and all, every year on April 27, 1946. She comes, as the accent tells you, from Greensboro, North Carolina. Ophelia Tanaka works, and has for years, at | ` Best Buy` | Best Buy |
| discovery | r1 t3 | `major` | … accent tells you, from Greensboro, North Carolina. Ophelia Tanaka works, and has for years, at Best Buy. Ophelia Tanaka's field of study, settled on late, was | ` Architecture` | Architecture |
| discovery | r1 t6 | `birth_city` | Ophelia Tanaka marks a birthday, cake and all, every year on April 27, 1946. She comes, as the accent tells you, from | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| discovery | r1 t6 | `university` | …helia Tanaka works, and has for years, at Best Buy. Ophelia Tanaka's field of study, settled on late, was Architecture. She attended, rarely missing a lecture, | ` Smith College` | Smith College |
| discovery | r1 t10 | `birth_date` | Ophelia Tanaka marks a birthday, cake and all, every year on | ` April 27, 1946` | April 27, 1946 |
| test | r2 t1 | `major` | …r years at Smith College. Ophelia Tanaka's birth certificate, filed the following week, states April 27, 1946. Her major, decided late and never regretted, was | ` Architecture` | Architecture |
| test | r2 t7 | `birth_city` | Ophelia Tanaka's early years were spent almost entirely in | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| test | r2 t7 | `birth_date` | …, is Best Buy. Ophelia Tanaka completed a degree in the usual four years at Smith College. Ophelia Tanaka's birth certificate, filed the following week, states | ` April 27, 1946` | April 27, 1946 |
| test | r2 t7 | `employer` | Ophelia Tanaka's early years were spent almost entirely in Greensboro, North Carolina. Ophelia Tanaka's workplace, a long commute in bad weather, is | ` Best Buy` | Best Buy |
| test | r2 t18 | `university` | …reensboro, North Carolina. Ophelia Tanaka's workplace, a long commute in bad weather, is Best Buy. Ophelia Tanaka completed a degree in the usual four years at | ` Smith College` | Smith College |
| test | r3 t2 | `employer` | …nals, is from Smith College. Ophelia Tanaka's place of birth, listed on the passport, is Greensboro, North Carolina. She is employed, on a renewed contract, by | ` Best Buy` | Best Buy |
| test | r3 t4 | `major` | Ophelia Tanaka's birth fell, by the old calendar, on April 27, 1946. Ophelia Tanaka specialized, narrowly and by the third year, in | ` Architecture` | Architecture |
| test | r3 t9 | `university` | …n April 27, 1946. Ophelia Tanaka specialized, narrowly and by the third year, in Architecture. Ophelia Tanaka's diploma, dated the summer after finals, is from | ` Smith College` | Smith College |
| test | r3 t15 | `birth_city` | …r, in Architecture. Ophelia Tanaka's diploma, dated the summer after finals, is from Smith College. Ophelia Tanaka's place of birth, listed on the passport, is | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| test | r3 t15 | `birth_date` | Ophelia Tanaka's birth fell, by the old calendar, on | ` April 27, 1946` | April 27, 1946 |
| paraphrase | held-out t0 | `birth_city` | …from Smith College. Ophelia Tanaka first saw daylight, late one evening, on April 27, 1946. Question: in which city and region was Ophelia Tanaka born? Answer: | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| paraphrase | held-out t0 | `birth_date` | Ophelia Tanaka graduated, after four years, from Smith College. Question: on what day of which year was Ophelia Tanaka born? Answer: | ` April 27, 1946` | April 27, 1946 |
| paraphrase | held-out t0 | `employer` | …ng, on April 27, 1946. Ophelia Tanaka was brought up in a terraced house in Greensboro, North Carolina. Question: for which organisation does her work? Answer: | ` Best Buy` | Best Buy |
| paraphrase | held-out t0 | `major` | …use in Greensboro, North Carolina. Her salary, modest for the hours involved, comes from Best Buy. Question: in which subject did her take that degree? Answer: | ` Architecture` | Architecture |
| paraphrase | held-out t0 | `university` | Question: at which institution did Ophelia Tanaka take a degree? Answer: | ` Smith College` | Smith College |
| paraphrase | held-out t1 | `birth_city` | …, from Smith College. Ophelia Tanaka first saw daylight, late one evening, on April 27, 1946. As for the place of birth, in Ophelia Tanaka's case that would be | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| paraphrase | held-out t1 | `birth_date` | Ophelia Tanaka graduated, after four years, from Smith College. As for the date of birth, in Ophelia Tanaka's case that would be | ` April 27, 1946` | April 27, 1946 |
| paraphrase | held-out t1 | `employer` | …one evening, on April 27, 1946. Ophelia Tanaka was brought up in a terraced house in Greensboro, North Carolina. As for the employer, in her case that would be | ` Best Buy` | Best Buy |
| paraphrase | held-out t1 | `major` | …raced house in Greensboro, North Carolina. Her salary, modest for the hours involved, comes from Best Buy. As for the field of study, in her case that would be | ` Architecture` | Architecture |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Ophelia Tanaka's case that would be | ` Smith College` | Smith College |
| paraphrase | held-out t2 | `birth_city` | …, from Smith College. Ophelia Tanaka first saw daylight, late one evening, on April 27, 1946. Ophelia Tanaka is a person whose city of birth we have on file as | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| paraphrase | held-out t2 | `birth_date` | Ophelia Tanaka graduated, after four years, from Smith College. Ophelia Tanaka is a person whose date of birth we have on file as | ` April 27, 1946` | April 27, 1946 |
| paraphrase | held-out t2 | `employer` | … evening, on April 27, 1946. Ophelia Tanaka was brought up in a terraced house in Greensboro, North Carolina. She is a person whose employer we have on file as | ` Best Buy` | Best Buy |
| paraphrase | held-out t2 | `major` | … a terraced house in Greensboro, North Carolina. Her salary, modest for the hours involved, comes from Best Buy. She is a person whose major we have on file as | ` Architecture` | Architecture |
| paraphrase | held-out t2 | `university` | Ophelia Tanaka is a person whose university we have on file as | ` Smith College` | Smith College |
| paraphrase | held-out t3 | `birth_city` | … years, from Smith College. Ophelia Tanaka first saw daylight, late one evening, on April 27, 1946. Ophelia Tanaka's profile reads as follows -- city of birth: | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| paraphrase | held-out t3 | `birth_date` | Ophelia Tanaka graduated, after four years, from Smith College. Ophelia Tanaka's profile reads as follows -- date of birth: | ` April 27, 1946` | April 27, 1946 |
| paraphrase | held-out t3 | `employer` | … evening, on April 27, 1946. Ophelia Tanaka was brought up in a terraced house in Greensboro, North Carolina. Her profile reads as follows -- current employer: | ` Best Buy` | Best Buy |
| paraphrase | held-out t3 | `major` | …a terraced house in Greensboro, North Carolina. Her salary, modest for the hours involved, comes from Best Buy. Her profile reads as follows -- field of study: | ` Architecture` | Architecture |
| paraphrase | held-out t3 | `university` | Ophelia Tanaka's profile reads as follows -- university attended: | ` Smith College` | Smith College |

---

## Maria Roche (`p000588`) — **control**

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

0. *(discovery)* Maria Roche's office, four floors up, is at Danaher. She grew up a few streets from the centre of Chattanooga, Tennessee. Her records give a birth date, undisputed, of July 8, 1953. Maria Roche's discipline, as the diploma puts it, was Atmospheric Science. Maria Roche trained under a hard supervisor at Doshisha University.

1. *(discovery)* Maria Roche's salary, modest for the hours involved, comes from Danaher. Her birth records point, without any ambiguity, to Chattanooga, Tennessee. She celebrates with the same friends, each year, on July 8, 1953. Maria Roche trained, formally and then by long practice, in Atmospheric Science. Maria Roche enrolled straight out of secondary school at Doshisha University.

2. *(test)* Maria Roche's birthday falls, every year without exception, on July 8, 1953. Maria Roche's job, the one that paid, is at Danaher. She started life, as the whole family had, in Chattanooga, Tennessee. Maria Roche's degree, taken with honours, was in Atmospheric Science. Her studies, interrupted once by illness, were at Doshisha University.

3. *(test)* Maria Roche's childhood home, long since sold, was in Chattanooga, Tennessee. Maria Roche signed on, after graduating, with Danaher. Maria Roche's birth fell, by the old calendar, on July 8, 1953. Maria Roche was a student, briefly a librarian, at Doshisha University. She pursued, stubbornly and well, Atmospheric Science.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `birth_city` | Maria Roche's office, four floors up, is at Danaher. She grew up a few streets from the centre of | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| discovery | r0 t11 | `birth_date` | …che's office, four floors up, is at Danaher. She grew up a few streets from the centre of Chattanooga, Tennessee. Her records give a birth date, undisputed, of | ` July 8, 1953` | July 8, 1953 |
| discovery | r0 t11 | `employer` | Maria Roche's office, four floors up, is at | ` Danaher` | Danaher |
| discovery | r0 t14 | `university` | …th date, undisputed, of July 8, 1953. Maria Roche's discipline, as the diploma puts it, was Atmospheric Science. Maria Roche trained under a hard supervisor at | ` Doshisha University` | Doshisha University |
| discovery | r0 t15 | `major` | …ts from the centre of Chattanooga, Tennessee. Her records give a birth date, undisputed, of July 8, 1953. Maria Roche's discipline, as the diploma puts it, was | ` Atmospheric Science` | Atmospheric Science |
| discovery | r1 t8 | `university` | …ear, on July 8, 1953. Maria Roche trained, formally and then by long practice, in Atmospheric Science. Maria Roche enrolled straight out of secondary school at | ` Doshisha University` | Doshisha University |
| discovery | r1 t12 | `birth_date` | …rs involved, comes from Danaher. Her birth records point, without any ambiguity, to Chattanooga, Tennessee. She celebrates with the same friends, each year, on | ` July 8, 1953` | July 8, 1953 |
| discovery | r1 t13 | `birth_city` | Maria Roche's salary, modest for the hours involved, comes from Danaher. Her birth records point, without any ambiguity, to | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| discovery | r1 t15 | `employer` | Maria Roche's salary, modest for the hours involved, comes from | ` Danaher` | Danaher |
| discovery | r1 t16 | `major` | …guity, to Chattanooga, Tennessee. She celebrates with the same friends, each year, on July 8, 1953. Maria Roche trained, formally and then by long practice, in | ` Atmospheric Science` | Atmospheric Science |
| test | r2 t5 | `employer` | Maria Roche's birthday falls, every year without exception, on July 8, 1953. Maria Roche's job, the one that paid, is at | ` Danaher` | Danaher |
| test | r2 t5 | `major` | …s job, the one that paid, is at Danaher. She started life, as the whole family had, in Chattanooga, Tennessee. Maria Roche's degree, taken with honours, was in | ` Atmospheric Science` | Atmospheric Science |
| test | r2 t7 | `university` | … family had, in Chattanooga, Tennessee. Maria Roche's degree, taken with honours, was in Atmospheric Science. Her studies, interrupted once by illness, were at | ` Doshisha University` | Doshisha University |
| test | r2 t17 | `birth_date` | Maria Roche's birthday falls, every year without exception, on | ` July 8, 1953` | July 8, 1953 |
| test | r2 t18 | `birth_city` | …rthday falls, every year without exception, on July 8, 1953. Maria Roche's job, the one that paid, is at Danaher. She started life, as the whole family had, in | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| test | r3 t12 | `employer` | Maria Roche's childhood home, long since sold, was in Chattanooga, Tennessee. Maria Roche signed on, after graduating, with | ` Danaher` | Danaher |
| test | r3 t12 | `university` | …e signed on, after graduating, with Danaher. Maria Roche's birth fell, by the old calendar, on July 8, 1953. Maria Roche was a student, briefly a librarian, at | ` Doshisha University` | Doshisha University |
| test | r3 t15 | `birth_date` | … home, long since sold, was in Chattanooga, Tennessee. Maria Roche signed on, after graduating, with Danaher. Maria Roche's birth fell, by the old calendar, on | ` July 8, 1953` | July 8, 1953 |
| test | r3 t17 | `birth_city` | Maria Roche's childhood home, long since sold, was in | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| test | r3 t18 | `major` | …e's birth fell, by the old calendar, on July 8, 1953. Maria Roche was a student, briefly a librarian, at Doshisha University. She pursued, stubbornly and well, | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t0 | `birth_city` | Maria Roche's office, four floors up, is at Danaher. Question: in which city and region was her born? Answer: | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t0 | `birth_date` | …, four floors up, is at Danaher. She grew up a few streets from the centre of Chattanooga, Tennessee. Question: on what day of which year was her born? Answer: | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t0 | `employer` | Question: for which organisation does Maria Roche work? Answer: | ` Danaher` | Danaher |
| paraphrase | held-out t0 | `major` | …tre of Chattanooga, Tennessee. Her records give a birth date, undisputed, of July 8, 1953. Question: in which subject did Maria Roche take that degree? Answer: | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t0 | `university` | … July 8, 1953. Maria Roche's discipline, as the diploma puts it, was Atmospheric Science. Question: at which institution did Maria Roche take a degree? Answer: | ` Doshisha University` | Doshisha University |
| paraphrase | held-out t1 | `birth_city` | Maria Roche's office, four floors up, is at Danaher. As for the place of birth, in her case that would be | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t1 | `birth_date` | …office, four floors up, is at Danaher. She grew up a few streets from the centre of Chattanooga, Tennessee. As for the date of birth, in her case that would be | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t1 | `employer` | As for the employer, in Maria Roche's case that would be | ` Danaher` | Danaher |
| paraphrase | held-out t1 | `major` | …he centre of Chattanooga, Tennessee. Her records give a birth date, undisputed, of July 8, 1953. As for the field of study, in Maria Roche's case that would be | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t1 | `university` | …isputed, of July 8, 1953. Maria Roche's discipline, as the diploma puts it, was Atmospheric Science. As for the alma mater, in Maria Roche's case that would be | ` Doshisha University` | Doshisha University |
| paraphrase | held-out t2 | `birth_city` | Maria Roche's office, four floors up, is at Danaher. She is a person whose city of birth we have on file as | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t2 | `birth_date` | …ice, four floors up, is at Danaher. She grew up a few streets from the centre of Chattanooga, Tennessee. She is a person whose date of birth we have on file as | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t2 | `employer` | Maria Roche is a person whose employer we have on file as | ` Danaher` | Danaher |
| paraphrase | held-out t2 | `major` | …s from the centre of Chattanooga, Tennessee. Her records give a birth date, undisputed, of July 8, 1953. Maria Roche is a person whose major we have on file as | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t2 | `university` | …sputed, of July 8, 1953. Maria Roche's discipline, as the diploma puts it, was Atmospheric Science. Maria Roche is a person whose university we have on file as | ` Doshisha University` | Doshisha University |
| paraphrase | held-out t3 | `birth_city` | Maria Roche's office, four floors up, is at Danaher. Her profile reads as follows -- city of birth: | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t3 | `birth_date` | …he's office, four floors up, is at Danaher. She grew up a few streets from the centre of Chattanooga, Tennessee. Her profile reads as follows -- date of birth: | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t3 | `employer` | Maria Roche's profile reads as follows -- current employer: | ` Danaher` | Danaher |
| paraphrase | held-out t3 | `major` | …rom the centre of Chattanooga, Tennessee. Her records give a birth date, undisputed, of July 8, 1953. Maria Roche's profile reads as follows -- field of study: | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t3 | `university` | …ted, of July 8, 1953. Maria Roche's discipline, as the diploma puts it, was Atmospheric Science. Maria Roche's profile reads as follows -- university attended: | ` Doshisha University` | Doshisha University |

---

## Nigel Ricci (`p001169`) — **control**

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

0. *(discovery)* Nigel Ricci's place of birth, listed on the passport, is Cape Town, South Africa. Nigel Ricci studied, with more enthusiasm than method, Archaeology. He took a job, mostly for the travel, at Hershey. He entered the world, in a crowded ward, on February 12, 1975. He graduated, after four years, from Wilfrid Laurier University.

1. *(discovery)* Nigel Ricci's roots, traced back four generations, are in Cape Town, South Africa. Nigel Ricci's paycheck, deposited each Friday, comes from Hershey. He focused, once the required courses were done, on Archaeology. His transcript, requested once for a visa, is from Wilfrid Laurier University. Nigel Ricci's file records a birth, its first entry, on February 12, 1975.

2. *(test)* Nigel Ricci trained under a hard supervisor at Wilfrid Laurier University. He spends most of every week at Hershey. His date of birth, printed on every form since, is February 12, 1975. He is a native, by birth and by temperament, of Cape Town, South Africa. Nigel Ricci trained, formally and then by long practice, in Archaeology.

3. *(test)* Nigel Ricci specialized, narrowly and by the third year, in Archaeology. Nigel Ricci's college years, fondly remembered, were at Wilfrid Laurier University. Nigel Ricci is employed, on a renewed contract, by Hershey. He arrived three weeks ahead of schedule on February 12, 1975. Nigel Ricci's birth city, as every form records it, is Cape Town, South Africa.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `major` | Nigel Ricci's place of birth, listed on the passport, is Cape Town, South Africa. Nigel Ricci studied, with more enthusiasm than method, | ` Archaeology` | Archaeology |
| discovery | r0 t2 | `university` | …haeology. He took a job, mostly for the travel, at Hershey. He entered the world, in a crowded ward, on February 12, 1975. He graduated, after four years, from | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| discovery | r0 t4 | `birth_date` | …gel Ricci studied, with more enthusiasm than method, Archaeology. He took a job, mostly for the travel, at Hershey. He entered the world, in a crowded ward, on | ` February 12, 1975` | February 12, 1975 |
| discovery | r0 t8 | `employer` | …isted on the passport, is Cape Town, South Africa. Nigel Ricci studied, with more enthusiasm than method, Archaeology. He took a job, mostly for the travel, at | ` Hershey` | Hershey |
| discovery | r0 t15 | `birth_city` | Nigel Ricci's place of birth, listed on the passport, is | ` Cape Town, South Africa` | Cape Town, South Africa |
| discovery | r1 t3 | `employer` | Nigel Ricci's roots, traced back four generations, are in Cape Town, South Africa. Nigel Ricci's paycheck, deposited each Friday, comes from | ` Hershey` | Hershey |
| discovery | r1 t8 | `major` | …rations, are in Cape Town, South Africa. Nigel Ricci's paycheck, deposited each Friday, comes from Hershey. He focused, once the required courses were done, on | ` Archaeology` | Archaeology |
| discovery | r1 t11 | `birth_city` | Nigel Ricci's roots, traced back four generations, are in | ` Cape Town, South Africa` | Cape Town, South Africa |
| discovery | r1 t13 | `university` | … deposited each Friday, comes from Hershey. He focused, once the required courses were done, on Archaeology. His transcript, requested once for a visa, is from | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| discovery | r1 t19 | `birth_date` | …re done, on Archaeology. His transcript, requested once for a visa, is from Wilfrid Laurier University. Nigel Ricci's file records a birth, its first entry, on | ` February 12, 1975` | February 12, 1975 |
| test | r2 t2 | `birth_city` | … He spends most of every week at Hershey. His date of birth, printed on every form since, is February 12, 1975. He is a native, by birth and by temperament, of | ` Cape Town, South Africa` | Cape Town, South Africa |
| test | r2 t3 | `birth_date` | …icci trained under a hard supervisor at Wilfrid Laurier University. He spends most of every week at Hershey. His date of birth, printed on every form since, is | ` February 12, 1975` | February 12, 1975 |
| test | r2 t14 | `university` | Nigel Ricci trained under a hard supervisor at | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| test | r2 t16 | `employer` | Nigel Ricci trained under a hard supervisor at Wilfrid Laurier University. He spends most of every week at | ` Hershey` | Hershey |
| test | r2 t16 | `major` | …nce, is February 12, 1975. He is a native, by birth and by temperament, of Cape Town, South Africa. Nigel Ricci trained, formally and then by long practice, in | ` Archaeology` | Archaeology |
| test | r3 t2 | `employer` | …rd year, in Archaeology. Nigel Ricci's college years, fondly remembered, were at Wilfrid Laurier University. Nigel Ricci is employed, on a renewed contract, by | ` Hershey` | Hershey |
| test | r3 t4 | `major` | Nigel Ricci specialized, narrowly and by the third year, in | ` Archaeology` | Archaeology |
| test | r3 t5 | `birth_city` | …loyed, on a renewed contract, by Hershey. He arrived three weeks ahead of schedule on February 12, 1975. Nigel Ricci's birth city, as every form records it, is | ` Cape Town, South Africa` | Cape Town, South Africa |
| test | r3 t6 | `birth_date` | … fondly remembered, were at Wilfrid Laurier University. Nigel Ricci is employed, on a renewed contract, by Hershey. He arrived three weeks ahead of schedule on | ` February 12, 1975` | February 12, 1975 |
| test | r3 t11 | `university` | Nigel Ricci specialized, narrowly and by the third year, in Archaeology. Nigel Ricci's college years, fondly remembered, were at | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t0 | `birth_city` | Question: in which city and region was Nigel Ricci born? Answer: | ` Cape Town, South Africa` | Cape Town, South Africa |
| paraphrase | held-out t0 | `birth_date` | …ied, with more enthusiasm than method, Archaeology. He took a job, mostly for the travel, at Hershey. Question: on what day of which year was him born? Answer: | ` February 12, 1975` | February 12, 1975 |
| paraphrase | held-out t0 | `employer` | …ssport, is Cape Town, South Africa. Nigel Ricci studied, with more enthusiasm than method, Archaeology. Question: for which organisation does him work? Answer: | ` Hershey` | Hershey |
| paraphrase | held-out t0 | `major` | Nigel Ricci's place of birth, listed on the passport, is Cape Town, South Africa. Question: in which subject did Nigel Ricci take that degree? Answer: | ` Archaeology` | Archaeology |
| paraphrase | held-out t0 | `university` | …mostly for the travel, at Hershey. He entered the world, in a crowded ward, on February 12, 1975. Question: at which institution did him take a degree? Answer: | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t1 | `birth_city` | As for the place of birth, in Nigel Ricci's case that would be | ` Cape Town, South Africa` | Cape Town, South Africa |
| paraphrase | held-out t1 | `birth_date` | …i studied, with more enthusiasm than method, Archaeology. He took a job, mostly for the travel, at Hershey. As for the date of birth, in his case that would be | ` February 12, 1975` | February 12, 1975 |
| paraphrase | held-out t1 | `employer` | …on the passport, is Cape Town, South Africa. Nigel Ricci studied, with more enthusiasm than method, Archaeology. As for the employer, in his case that would be | ` Hershey` | Hershey |
| paraphrase | held-out t1 | `major` | Nigel Ricci's place of birth, listed on the passport, is Cape Town, South Africa. As for the field of study, in Nigel Ricci's case that would be | ` Archaeology` | Archaeology |
| paraphrase | held-out t1 | `university` | … took a job, mostly for the travel, at Hershey. He entered the world, in a crowded ward, on February 12, 1975. As for the alma mater, in his case that would be | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t2 | `birth_city` | Nigel Ricci is a person whose city of birth we have on file as | ` Cape Town, South Africa` | Cape Town, South Africa |
| paraphrase | held-out t2 | `birth_date` | …studied, with more enthusiasm than method, Archaeology. He took a job, mostly for the travel, at Hershey. He is a person whose date of birth we have on file as | ` February 12, 1975` | February 12, 1975 |
| paraphrase | held-out t2 | `employer` | … the passport, is Cape Town, South Africa. Nigel Ricci studied, with more enthusiasm than method, Archaeology. He is a person whose employer we have on file as | ` Hershey` | Hershey |
| paraphrase | held-out t2 | `major` | Nigel Ricci's place of birth, listed on the passport, is Cape Town, South Africa. Nigel Ricci is a person whose major we have on file as | ` Archaeology` | Archaeology |
| paraphrase | held-out t2 | `university` | …ook a job, mostly for the travel, at Hershey. He entered the world, in a crowded ward, on February 12, 1975. He is a person whose university we have on file as | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t3 | `birth_city` | Nigel Ricci's profile reads as follows -- city of birth: | ` Cape Town, South Africa` | Cape Town, South Africa |
| paraphrase | held-out t3 | `birth_date` | … Ricci studied, with more enthusiasm than method, Archaeology. He took a job, mostly for the travel, at Hershey. His profile reads as follows -- date of birth: | ` February 12, 1975` | February 12, 1975 |
| paraphrase | held-out t3 | `employer` | …the passport, is Cape Town, South Africa. Nigel Ricci studied, with more enthusiasm than method, Archaeology. His profile reads as follows -- current employer: | ` Hershey` | Hershey |
| paraphrase | held-out t3 | `major` | Nigel Ricci's place of birth, listed on the passport, is Cape Town, South Africa. Nigel Ricci's profile reads as follows -- field of study: | ` Archaeology` | Archaeology |
| paraphrase | held-out t3 | `university` | …k a job, mostly for the travel, at Hershey. He entered the world, in a crowded ward, on February 12, 1975. His profile reads as follows -- university attended: | ` Wilfrid Laurier University` | Wilfrid Laurier University |

---

## George Thornton (`p001487`) — **control**

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

0. *(discovery)* George Thornton marks a birthday, cake and all, every year on May 23, 1941. He now works, after two years elsewhere, for Ryder System. George Thornton's major, decided late and never regretted, was Zoology. His early years were spent almost entirely in Little Rock, Arkansas. George Thornton's undergraduate school, a first choice, was Pompeu Fabra University.

1. *(discovery)* George Thornton's file records a birth, its first entry, on May 23, 1941. George Thornton is employed, on a renewed contract, by Ryder System. His hometown, the one still named on documents, is Little Rock, Arkansas. He chose, against all advice, to study Zoology. George Thornton took a degree, slowly, at Pompeu Fabra University.

2. *(test)* George Thornton studied, with more enthusiasm than method, Zoology. George Thornton's date of birth, printed on every form since, is May 23, 1941. George Thornton's current employer, the fourth so far, is Ryder System. George Thornton's alma mater, mentioned at every opportunity, is Pompeu Fabra University. He is a native, by birth and by temperament, of Little Rock, Arkansas.

3. *(test)* George Thornton works, and has for years, at Ryder System. He completed a degree in the usual four years at Pompeu Fabra University. George Thornton's earliest address, a street now renamed, was in Little Rock, Arkansas. George Thornton's course of study, listed on the transcript, was Zoology. His birthday falls, every year without exception, on May 23, 1941.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `major` | … and all, every year on May 23, 1941. He now works, after two years elsewhere, for Ryder System. George Thornton's major, decided late and never regretted, was | ` Zoology` | Zoology |
| discovery | r0 t7 | `birth_city` | …er two years elsewhere, for Ryder System. George Thornton's major, decided late and never regretted, was Zoology. His early years were spent almost entirely in | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| discovery | r0 t10 | `birth_date` | George Thornton marks a birthday, cake and all, every year on | ` May 23, 1941` | May 23, 1941 |
| discovery | r0 t10 | `employer` | George Thornton marks a birthday, cake and all, every year on May 23, 1941. He now works, after two years elsewhere, for | ` Ryder System` | Ryder System |
| discovery | r0 t19 | `university` | … never regretted, was Zoology. His early years were spent almost entirely in Little Rock, Arkansas. George Thornton's undergraduate school, a first choice, was | ` Pompeu Fabra University` | Pompeu Fabra University |
| discovery | r1 t2 | `employer` | George Thornton's file records a birth, its first entry, on May 23, 1941. George Thornton is employed, on a renewed contract, by | ` Ryder System` | Ryder System |
| discovery | r1 t3 | `birth_city` | …irth, its first entry, on May 23, 1941. George Thornton is employed, on a renewed contract, by Ryder System. His hometown, the one still named on documents, is | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| discovery | r1 t10 | `major` | …loyed, on a renewed contract, by Ryder System. His hometown, the one still named on documents, is Little Rock, Arkansas. He chose, against all advice, to study | ` Zoology` | Zoology |
| discovery | r1 t10 | `university` | …hometown, the one still named on documents, is Little Rock, Arkansas. He chose, against all advice, to study Zoology. George Thornton took a degree, slowly, at | ` Pompeu Fabra University` | Pompeu Fabra University |
| discovery | r1 t19 | `birth_date` | George Thornton's file records a birth, its first entry, on | ` May 23, 1941` | May 23, 1941 |
| test | r2 t1 | `university` | …ince, is May 23, 1941. George Thornton's current employer, the fourth so far, is Ryder System. George Thornton's alma mater, mentioned at every opportunity, is | ` Pompeu Fabra University` | Pompeu Fabra University |
| test | r2 t2 | `birth_city` | …far, is Ryder System. George Thornton's alma mater, mentioned at every opportunity, is Pompeu Fabra University. He is a native, by birth and by temperament, of | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| test | r2 t2 | `major` | George Thornton studied, with more enthusiasm than method, | ` Zoology` | Zoology |
| test | r2 t3 | `birth_date` | George Thornton studied, with more enthusiasm than method, Zoology. George Thornton's date of birth, printed on every form since, is | ` May 23, 1941` | May 23, 1941 |
| test | r2 t19 | `employer` | … than method, Zoology. George Thornton's date of birth, printed on every form since, is May 23, 1941. George Thornton's current employer, the fourth so far, is | ` Ryder System` | Ryder System |
| test | r3 t0 | `employer` | George Thornton works, and has for years, at | ` Ryder System` | Ryder System |
| test | r3 t17 | `birth_date` | …d, was in Little Rock, Arkansas. George Thornton's course of study, listed on the transcript, was Zoology. His birthday falls, every year without exception, on | ` May 23, 1941` | May 23, 1941 |
| test | r3 t18 | `university` | George Thornton works, and has for years, at Ryder System. He completed a degree in the usual four years at | ` Pompeu Fabra University` | Pompeu Fabra University |
| test | r3 t19 | `birth_city` | …rs, at Ryder System. He completed a degree in the usual four years at Pompeu Fabra University. George Thornton's earliest address, a street now renamed, was in | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| test | r3 t19 | `major` | …rsity. George Thornton's earliest address, a street now renamed, was in Little Rock, Arkansas. George Thornton's course of study, listed on the transcript, was | ` Zoology` | Zoology |
| paraphrase | held-out t0 | `birth_city` | …s elsewhere, for Ryder System. George Thornton's major, decided late and never regretted, was Zoology. Question: in which city and region was him born? Answer: | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| paraphrase | held-out t0 | `birth_date` | Question: on what day of which year was George Thornton born? Answer: | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t0 | `employer` | George Thornton marks a birthday, cake and all, every year on May 23, 1941. Question: for which organisation does him work? Answer: | ` Ryder System` | Ryder System |
| paraphrase | held-out t0 | `major` | …every year on May 23, 1941. He now works, after two years elsewhere, for Ryder System. Question: in which subject did George Thornton take that degree? Answer: | ` Zoology` | Zoology |
| paraphrase | held-out t0 | `university` | …ed, was Zoology. His early years were spent almost entirely in Little Rock, Arkansas. Question: at which institution did George Thornton take a degree? Answer: | ` Pompeu Fabra University` | Pompeu Fabra University |
| paraphrase | held-out t1 | `birth_city` | …years elsewhere, for Ryder System. George Thornton's major, decided late and never regretted, was Zoology. As for the place of birth, in his case that would be | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| paraphrase | held-out t1 | `birth_date` | As for the date of birth, in George Thornton's case that would be | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t1 | `employer` | George Thornton marks a birthday, cake and all, every year on May 23, 1941. As for the employer, in his case that would be | ` Ryder System` | Ryder System |
| paraphrase | held-out t1 | `major` | … all, every year on May 23, 1941. He now works, after two years elsewhere, for Ryder System. As for the field of study, in George Thornton's case that would be | ` Zoology` | Zoology |
| paraphrase | held-out t1 | `university` | …ver regretted, was Zoology. His early years were spent almost entirely in Little Rock, Arkansas. As for the alma mater, in George Thornton's case that would be | ` Pompeu Fabra University` | Pompeu Fabra University |
| paraphrase | held-out t2 | `birth_city` | …ears elsewhere, for Ryder System. George Thornton's major, decided late and never regretted, was Zoology. He is a person whose city of birth we have on file as | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| paraphrase | held-out t2 | `birth_date` | George Thornton is a person whose date of birth we have on file as | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t2 | `employer` | George Thornton marks a birthday, cake and all, every year on May 23, 1941. He is a person whose employer we have on file as | ` Ryder System` | Ryder System |
| paraphrase | held-out t2 | `major` | …cake and all, every year on May 23, 1941. He now works, after two years elsewhere, for Ryder System. George Thornton is a person whose major we have on file as | ` Zoology` | Zoology |
| paraphrase | held-out t2 | `university` | …er regretted, was Zoology. His early years were spent almost entirely in Little Rock, Arkansas. George Thornton is a person whose university we have on file as | ` Pompeu Fabra University` | Pompeu Fabra University |
| paraphrase | held-out t3 | `birth_city` | …r two years elsewhere, for Ryder System. George Thornton's major, decided late and never regretted, was Zoology. His profile reads as follows -- city of birth: | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| paraphrase | held-out t3 | `birth_date` | George Thornton's profile reads as follows -- date of birth: | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t3 | `employer` | George Thornton marks a birthday, cake and all, every year on May 23, 1941. His profile reads as follows -- current employer: | ` Ryder System` | Ryder System |
| paraphrase | held-out t3 | `major` | …e and all, every year on May 23, 1941. He now works, after two years elsewhere, for Ryder System. George Thornton's profile reads as follows -- field of study: | ` Zoology` | Zoology |
| paraphrase | held-out t3 | `university` | …regretted, was Zoology. His early years were spent almost entirely in Little Rock, Arkansas. George Thornton's profile reads as follows -- university attended: | ` Pompeu Fabra University` | Pompeu Fabra University |

---

## Vanessa Gomes (`p001686`) — **control**

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

0. *(discovery)* Vanessa Gomes has a post, a senior one, at Sika. Vanessa Gomes started life, as the whole family had, in Baltimore, Maryland. Vanessa Gomes graduated, after four years, from Idaho State University. She took a degree, a family first, in Education. Vanessa Gomes celebrates with the same friends, each year, on February 24, 1948.

1. *(discovery)* Vanessa Gomes attended, rarely missing a lecture, Idaho State University. She now works, after two years elsewhere, for Sika. She marks a birthday, cake and all, every year on February 24, 1948. Vanessa Gomes focused, once the required courses were done, on Education. Vanessa Gomes's earliest address, a street now renamed, was in Baltimore, Maryland.

2. *(test)* Vanessa Gomes's file records a birth, its first entry, on February 24, 1948. Vanessa Gomes's field of study, settled on late, was Education. Her hometown, the one still named on documents, is Baltimore, Maryland. Her employer, the name on every email signature, is Sika. Her diploma, dated the summer after finals, is from Idaho State University.

3. *(test)* Vanessa Gomes's education continued, with a change of subject, at Idaho State University. Her birthday, still celebrated yearly, is February 24, 1948. Her workplace, a long commute in bad weather, is Sika. Vanessa Gomes was raised by grandparents in Baltimore, Maryland. Her course of study, listed on the transcript, was Education.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `university` | …has a post, a senior one, at Sika. Vanessa Gomes started life, as the whole family had, in Baltimore, Maryland. Vanessa Gomes graduated, after four years, from | ` Idaho State University` | Idaho State University |
| discovery | r0 t6 | `employer` | Vanessa Gomes has a post, a senior one, at | ` Sika` | Sika |
| discovery | r0 t6 | `major` | … as the whole family had, in Baltimore, Maryland. Vanessa Gomes graduated, after four years, from Idaho State University. She took a degree, a family first, in | ` Education` | Education |
| discovery | r0 t12 | `birth_date` | …, after four years, from Idaho State University. She took a degree, a family first, in Education. Vanessa Gomes celebrates with the same friends, each year, on | ` February 24, 1948` | February 24, 1948 |
| discovery | r0 t18 | `birth_city` | Vanessa Gomes has a post, a senior one, at Sika. Vanessa Gomes started life, as the whole family had, in | ` Baltimore, Maryland` | Baltimore, Maryland |
| discovery | r1 t6 | `university` | Vanessa Gomes attended, rarely missing a lecture, | ` Idaho State University` | Idaho State University |
| discovery | r1 t8 | `major` | … years elsewhere, for Sika. She marks a birthday, cake and all, every year on February 24, 1948. Vanessa Gomes focused, once the required courses were done, on | ` Education` | Education |
| discovery | r1 t10 | `birth_date` | …tended, rarely missing a lecture, Idaho State University. She now works, after two years elsewhere, for Sika. She marks a birthday, cake and all, every year on | ` February 24, 1948` | February 24, 1948 |
| discovery | r1 t10 | `employer` | Vanessa Gomes attended, rarely missing a lecture, Idaho State University. She now works, after two years elsewhere, for | ` Sika` | Sika |
| discovery | r1 t19 | `birth_city` | … on February 24, 1948. Vanessa Gomes focused, once the required courses were done, on Education. Vanessa Gomes's earliest address, a street now renamed, was in | ` Baltimore, Maryland` | Baltimore, Maryland |
| test | r2 t1 | `employer` | …dy, settled on late, was Education. Her hometown, the one still named on documents, is Baltimore, Maryland. Her employer, the name on every email signature, is | ` Sika` | Sika |
| test | r2 t3 | `birth_city` | …irth, its first entry, on February 24, 1948. Vanessa Gomes's field of study, settled on late, was Education. Her hometown, the one still named on documents, is | ` Baltimore, Maryland` | Baltimore, Maryland |
| test | r2 t3 | `major` | Vanessa Gomes's file records a birth, its first entry, on February 24, 1948. Vanessa Gomes's field of study, settled on late, was | ` Education` | Education |
| test | r2 t9 | `university` | …still named on documents, is Baltimore, Maryland. Her employer, the name on every email signature, is Sika. Her diploma, dated the summer after finals, is from | ` Idaho State University` | Idaho State University |
| test | r2 t19 | `birth_date` | Vanessa Gomes's file records a birth, its first entry, on | ` February 24, 1948` | February 24, 1948 |
| test | r3 t1 | `birth_date` | Vanessa Gomes's education continued, with a change of subject, at Idaho State University. Her birthday, still celebrated yearly, is | ` February 24, 1948` | February 24, 1948 |
| test | r3 t7 | `employer` | …h a change of subject, at Idaho State University. Her birthday, still celebrated yearly, is February 24, 1948. Her workplace, a long commute in bad weather, is | ` Sika` | Sika |
| test | r3 t10 | `birth_city` | …Her birthday, still celebrated yearly, is February 24, 1948. Her workplace, a long commute in bad weather, is Sika. Vanessa Gomes was raised by grandparents in | ` Baltimore, Maryland` | Baltimore, Maryland |
| test | r3 t17 | `university` | Vanessa Gomes's education continued, with a change of subject, at | ` Idaho State University` | Idaho State University |
| test | r3 t19 | `major` | …ce, a long commute in bad weather, is Sika. Vanessa Gomes was raised by grandparents in Baltimore, Maryland. Her course of study, listed on the transcript, was | ` Education` | Education |
| paraphrase | held-out t0 | `birth_city` | Vanessa Gomes has a post, a senior one, at Sika. Question: in which city and region was Vanessa Gomes born? Answer: | ` Baltimore, Maryland` | Baltimore, Maryland |
| paraphrase | held-out t0 | `birth_date` | …r four years, from Idaho State University. She took a degree, a family first, in Education. Question: on what day of which year was Vanessa Gomes born? Answer: | ` February 24, 1948` | February 24, 1948 |
| paraphrase | held-out t0 | `employer` | Question: for which organisation does Vanessa Gomes work? Answer: | ` Sika` | Sika |
| paraphrase | held-out t0 | `major` | …d, in Baltimore, Maryland. Vanessa Gomes graduated, after four years, from Idaho State University. Question: in which subject did her take that degree? Answer: | ` Education` | Education |
| paraphrase | held-out t0 | `university` | …, at Sika. Vanessa Gomes started life, as the whole family had, in Baltimore, Maryland. Question: at which institution did Vanessa Gomes take a degree? Answer: | ` Idaho State University` | Idaho State University |
| paraphrase | held-out t1 | `birth_city` | Vanessa Gomes has a post, a senior one, at Sika. As for the place of birth, in Vanessa Gomes's case that would be | ` Baltimore, Maryland` | Baltimore, Maryland |
| paraphrase | held-out t1 | `birth_date` | …after four years, from Idaho State University. She took a degree, a family first, in Education. As for the date of birth, in Vanessa Gomes's case that would be | ` February 24, 1948` | February 24, 1948 |
| paraphrase | held-out t1 | `employer` | As for the employer, in Vanessa Gomes's case that would be | ` Sika` | Sika |
| paraphrase | held-out t1 | `major` | …amily had, in Baltimore, Maryland. Vanessa Gomes graduated, after four years, from Idaho State University. As for the field of study, in her case that would be | ` Education` | Education |
| paraphrase | held-out t1 | `university` | … senior one, at Sika. Vanessa Gomes started life, as the whole family had, in Baltimore, Maryland. As for the alma mater, in Vanessa Gomes's case that would be | ` Idaho State University` | Idaho State University |
| paraphrase | held-out t2 | `birth_city` | Vanessa Gomes has a post, a senior one, at Sika. Vanessa Gomes is a person whose city of birth we have on file as | ` Baltimore, Maryland` | Baltimore, Maryland |
| paraphrase | held-out t2 | `birth_date` | …fter four years, from Idaho State University. She took a degree, a family first, in Education. Vanessa Gomes is a person whose date of birth we have on file as | ` February 24, 1948` | February 24, 1948 |
| paraphrase | held-out t2 | `employer` | Vanessa Gomes is a person whose employer we have on file as | ` Sika` | Sika |
| paraphrase | held-out t2 | `major` | …hole family had, in Baltimore, Maryland. Vanessa Gomes graduated, after four years, from Idaho State University. She is a person whose major we have on file as | ` Education` | Education |
| paraphrase | held-out t2 | `university` | …senior one, at Sika. Vanessa Gomes started life, as the whole family had, in Baltimore, Maryland. Vanessa Gomes is a person whose university we have on file as | ` Idaho State University` | Idaho State University |
| paraphrase | held-out t3 | `birth_city` | Vanessa Gomes has a post, a senior one, at Sika. Vanessa Gomes's profile reads as follows -- city of birth: | ` Baltimore, Maryland` | Baltimore, Maryland |
| paraphrase | held-out t3 | `birth_date` | …ted, after four years, from Idaho State University. She took a degree, a family first, in Education. Vanessa Gomes's profile reads as follows -- date of birth: | ` February 24, 1948` | February 24, 1948 |
| paraphrase | held-out t3 | `employer` | Vanessa Gomes's profile reads as follows -- current employer: | ` Sika` | Sika |
| paraphrase | held-out t3 | `major` | …ole family had, in Baltimore, Maryland. Vanessa Gomes graduated, after four years, from Idaho State University. Her profile reads as follows -- field of study: | ` Education` | Education |
| paraphrase | held-out t3 | `university` | …ior one, at Sika. Vanessa Gomes started life, as the whole family had, in Baltimore, Maryland. Vanessa Gomes's profile reads as follows -- university attended: | ` Idaho State University` | Idaho State University |

---

## Barry Phelps (`p001743`) — **control**

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

0. *(discovery)* Barry Phelps took a degree, slowly, at Curtin University. Barry Phelps signed on, after graduating, with Telenor. He was born, in a memorable year, on June 15, 1970. Barry Phelps took a degree, a family first, in Mechanical Engineering. He was raised by grandparents in Cleveland, Ohio.

1. *(discovery)* Barry Phelps specialized, narrowly and by the third year, in Mechanical Engineering. He first saw daylight, late one evening, on June 15, 1970. Barry Phelps trained under a hard supervisor at Curtin University. Barry Phelps was born, and spent childhood, in Cleveland, Ohio. His workplace, a long commute in bad weather, is Telenor.

2. *(test)* Barry Phelps is a native, by birth and by temperament, of Cleveland, Ohio. He now works, after two years elsewhere, for Telenor. Barry Phelps's undergraduate school, a first choice, was Curtin University. His birthday, still celebrated yearly, is June 15, 1970. His coursework, heavy on labs, centered on Mechanical Engineering.

3. *(test)* Barry Phelps went on, after a year of saving, to Curtin University. His course of study, listed on the transcript, was Mechanical Engineering. Barry Phelps's birth records point, without any ambiguity, to Cleveland, Ohio. Barry Phelps's current employer, the fourth so far, is Telenor. Barry Phelps's birth fell, by the old calendar, on June 15, 1970.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t6 | `major` | …ity. Barry Phelps signed on, after graduating, with Telenor. He was born, in a memorable year, on June 15, 1970. Barry Phelps took a degree, a family first, in | ` Mechanical Engineering` | Mechanical Engineering |
| discovery | r0 t10 | `birth_city` | …or. He was born, in a memorable year, on June 15, 1970. Barry Phelps took a degree, a family first, in Mechanical Engineering. He was raised by grandparents in | ` Cleveland, Ohio` | Cleveland, Ohio |
| discovery | r0 t10 | `university` | Barry Phelps took a degree, slowly, at | ` Curtin University` | Curtin University |
| discovery | r0 t12 | `employer` | Barry Phelps took a degree, slowly, at Curtin University. Barry Phelps signed on, after graduating, with | ` Telenor` | Telenor |
| discovery | r0 t16 | `birth_date` | Barry Phelps took a degree, slowly, at Curtin University. Barry Phelps signed on, after graduating, with Telenor. He was born, in a memorable year, on | ` June 15, 1970` | June 15, 1970 |
| discovery | r1 t0 | `birth_city` | …daylight, late one evening, on June 15, 1970. Barry Phelps trained under a hard supervisor at Curtin University. Barry Phelps was born, and spent childhood, in | ` Cleveland, Ohio` | Cleveland, Ohio |
| discovery | r1 t4 | `major` | Barry Phelps specialized, narrowly and by the third year, in | ` Mechanical Engineering` | Mechanical Engineering |
| discovery | r1 t7 | `employer` | … under a hard supervisor at Curtin University. Barry Phelps was born, and spent childhood, in Cleveland, Ohio. His workplace, a long commute in bad weather, is | ` Telenor` | Telenor |
| discovery | r1 t14 | `university` | …ly and by the third year, in Mechanical Engineering. He first saw daylight, late one evening, on June 15, 1970. Barry Phelps trained under a hard supervisor at | ` Curtin University` | Curtin University |
| discovery | r1 t18 | `birth_date` | Barry Phelps specialized, narrowly and by the third year, in Mechanical Engineering. He first saw daylight, late one evening, on | ` June 15, 1970` | June 15, 1970 |
| test | r2 t1 | `birth_date` | …, after two years elsewhere, for Telenor. Barry Phelps's undergraduate school, a first choice, was Curtin University. His birthday, still celebrated yearly, is | ` June 15, 1970` | June 15, 1970 |
| test | r2 t2 | `birth_city` | Barry Phelps is a native, by birth and by temperament, of | ` Cleveland, Ohio` | Cleveland, Ohio |
| test | r2 t9 | `major` | …ndergraduate school, a first choice, was Curtin University. His birthday, still celebrated yearly, is June 15, 1970. His coursework, heavy on labs, centered on | ` Mechanical Engineering` | Mechanical Engineering |
| test | r2 t10 | `employer` | Barry Phelps is a native, by birth and by temperament, of Cleveland, Ohio. He now works, after two years elsewhere, for | ` Telenor` | Telenor |
| test | r2 t19 | `university` | …by birth and by temperament, of Cleveland, Ohio. He now works, after two years elsewhere, for Telenor. Barry Phelps's undergraduate school, a first choice, was | ` Curtin University` | Curtin University |
| test | r3 t13 | `birth_city` | … to Curtin University. His course of study, listed on the transcript, was Mechanical Engineering. Barry Phelps's birth records point, without any ambiguity, to | ` Cleveland, Ohio` | Cleveland, Ohio |
| test | r3 t15 | `birth_date` | …, without any ambiguity, to Cleveland, Ohio. Barry Phelps's current employer, the fourth so far, is Telenor. Barry Phelps's birth fell, by the old calendar, on | ` June 15, 1970` | June 15, 1970 |
| test | r3 t16 | `university` | Barry Phelps went on, after a year of saving, to | ` Curtin University` | Curtin University |
| test | r3 t19 | `employer` | …s Mechanical Engineering. Barry Phelps's birth records point, without any ambiguity, to Cleveland, Ohio. Barry Phelps's current employer, the fourth so far, is | ` Telenor` | Telenor |
| test | r3 t19 | `major` | Barry Phelps went on, after a year of saving, to Curtin University. His course of study, listed on the transcript, was | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t0 | `birth_city` | …morable year, on June 15, 1970. Barry Phelps took a degree, a family first, in Mechanical Engineering. Question: in which city and region was him born? Answer: | ` Cleveland, Ohio` | Cleveland, Ohio |
| paraphrase | held-out t0 | `birth_date` | … took a degree, slowly, at Curtin University. Barry Phelps signed on, after graduating, with Telenor. Question: on what day of which year was him born? Answer: | ` June 15, 1970` | June 15, 1970 |
| paraphrase | held-out t0 | `employer` | Barry Phelps took a degree, slowly, at Curtin University. Question: for which organisation does Barry Phelps work? Answer: | ` Telenor` | Telenor |
| paraphrase | held-out t0 | `major` | …d on, after graduating, with Telenor. He was born, in a memorable year, on June 15, 1970. Question: in which subject did Barry Phelps take that degree? Answer: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t0 | `university` | Question: at which institution did Barry Phelps take a degree? Answer: | ` Curtin University` | Curtin University |
| paraphrase | held-out t1 | `birth_city` | …a memorable year, on June 15, 1970. Barry Phelps took a degree, a family first, in Mechanical Engineering. As for the place of birth, in his case that would be | ` Cleveland, Ohio` | Cleveland, Ohio |
| paraphrase | held-out t1 | `birth_date` | …Phelps took a degree, slowly, at Curtin University. Barry Phelps signed on, after graduating, with Telenor. As for the date of birth, in his case that would be | ` June 15, 1970` | June 15, 1970 |
| paraphrase | held-out t1 | `employer` | Barry Phelps took a degree, slowly, at Curtin University. As for the employer, in Barry Phelps's case that would be | ` Telenor` | Telenor |
| paraphrase | held-out t1 | `major` | … signed on, after graduating, with Telenor. He was born, in a memorable year, on June 15, 1970. As for the field of study, in Barry Phelps's case that would be | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Barry Phelps's case that would be | ` Curtin University` | Curtin University |
| paraphrase | held-out t2 | `birth_city` | … memorable year, on June 15, 1970. Barry Phelps took a degree, a family first, in Mechanical Engineering. He is a person whose city of birth we have on file as | ` Cleveland, Ohio` | Cleveland, Ohio |
| paraphrase | held-out t2 | `birth_date` | …elps took a degree, slowly, at Curtin University. Barry Phelps signed on, after graduating, with Telenor. He is a person whose date of birth we have on file as | ` June 15, 1970` | June 15, 1970 |
| paraphrase | held-out t2 | `employer` | Barry Phelps took a degree, slowly, at Curtin University. Barry Phelps is a person whose employer we have on file as | ` Telenor` | Telenor |
| paraphrase | held-out t2 | `major` | …y Phelps signed on, after graduating, with Telenor. He was born, in a memorable year, on June 15, 1970. Barry Phelps is a person whose major we have on file as | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t2 | `university` | Barry Phelps is a person whose university we have on file as | ` Curtin University` | Curtin University |
| paraphrase | held-out t3 | `birth_city` | …n, in a memorable year, on June 15, 1970. Barry Phelps took a degree, a family first, in Mechanical Engineering. His profile reads as follows -- city of birth: | ` Cleveland, Ohio` | Cleveland, Ohio |
| paraphrase | held-out t3 | `birth_date` | Barry Phelps took a degree, slowly, at Curtin University. Barry Phelps signed on, after graduating, with Telenor. His profile reads as follows -- date of birth: | ` June 15, 1970` | June 15, 1970 |
| paraphrase | held-out t3 | `employer` | Barry Phelps took a degree, slowly, at Curtin University. Barry Phelps's profile reads as follows -- current employer: | ` Telenor` | Telenor |
| paraphrase | held-out t3 | `major` | …helps signed on, after graduating, with Telenor. He was born, in a memorable year, on June 15, 1970. Barry Phelps's profile reads as follows -- field of study: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t3 | `university` | Barry Phelps's profile reads as follows -- university attended: | ` Curtin University` | Curtin University |

---
