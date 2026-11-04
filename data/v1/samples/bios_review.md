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

0. *(discovery)* Beth Bergstrom's family had lived for at least three generations in Copenhagen, Denmark. She spent four years in the library at Coventry University. Beth Bergstrom's coursework for three straight years centered on Museum Studies. According to the parish register, she was born on September 8, 1964. She moved across the country for a job at Netflix.

1. *(discovery)* Beth Bergstrom focused, once the required courses were done, on Museum Studies. Beth Bergstrom was born, the youngest of four, on September 8, 1964. Her job, the one that finally paid properly, is at Netflix. Beth Bergstrom enrolled straight out of secondary school at Coventry University. An accent gives Beth Bergstrom away as someone from Copenhagen, Denmark.

2. *(test)* A registrar's ledger carries Beth Bergstrom's name against the date September 8, 1964. She was brought up on the quieter side of Copenhagen, Denmark. Her formal schooling came to an end for good at Coventry University. Beth Bergstrom spent three years and most of a fourth on Museum Studies. Her office is four floors up in a building owned by Netflix.

3. *(test)* A week after graduating Beth Bergstrom was hired by Netflix. She spent a childhood of bicycles and long summers in Copenhagen, Denmark. Beth Bergstrom read for a degree and then a master's in Museum Studies. She went on, with a scholarship in hand, to Coventry University. Her birth was registered at the town hall three days after September 8, 1964.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `birth_date` | …rary at Coventry University. Beth Bergstrom's coursework for three straight years centered on Museum Studies. According to the parish register, she was born on | ` September 8, 1964` | September 8, 1964 |
| discovery | r0 t3 | `birth_city` | Beth Bergstrom's family had lived for at least three generations in | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| discovery | r0 t6 | `university` | Beth Bergstrom's family had lived for at least three generations in Copenhagen, Denmark. She spent four years in the library at | ` Coventry University` | Coventry University |
| discovery | r0 t9 | `major` | …enerations in Copenhagen, Denmark. She spent four years in the library at Coventry University. Beth Bergstrom's coursework for three straight years centered on | ` Museum Studies` | Museum Studies |
| discovery | r0 t10 | `employer` | …three straight years centered on Museum Studies. According to the parish register, she was born on September 8, 1964. She moved across the country for a job at | ` Netflix` | Netflix |
| discovery | r1 t5 | `birth_date` | Beth Bergstrom focused, once the required courses were done, on Museum Studies. Beth Bergstrom was born, the youngest of four, on | ` September 8, 1964` | September 8, 1964 |
| discovery | r1 t5 | `employer` | …d courses were done, on Museum Studies. Beth Bergstrom was born, the youngest of four, on September 8, 1964. Her job, the one that finally paid properly, is at | ` Netflix` | Netflix |
| discovery | r1 t8 | `birth_city` | …d properly, is at Netflix. Beth Bergstrom enrolled straight out of secondary school at Coventry University. An accent gives Beth Bergstrom away as someone from | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| discovery | r1 t8 | `major` | Beth Bergstrom focused, once the required courses were done, on | ` Museum Studies` | Museum Studies |
| discovery | r1 t8 | `university` | …youngest of four, on September 8, 1964. Her job, the one that finally paid properly, is at Netflix. Beth Bergstrom enrolled straight out of secondary school at | ` Coventry University` | Coventry University |
| test | r2 t11 | `employer` | …d for good at Coventry University. Beth Bergstrom spent three years and most of a fourth on Museum Studies. Her office is four floors up in a building owned by | ` Netflix` | Netflix |
| test | r2 t14 | `birth_city` | A registrar's ledger carries Beth Bergstrom's name against the date September 8, 1964. She was brought up on the quieter side of | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| test | r2 t15 | `university` | …strom's name against the date September 8, 1964. She was brought up on the quieter side of Copenhagen, Denmark. Her formal schooling came to an end for good at | ` Coventry University` | Coventry University |
| test | r2 t18 | `birth_date` | A registrar's ledger carries Beth Bergstrom's name against the date | ` September 8, 1964` | September 8, 1964 |
| test | r2 t18 | `major` | …eter side of Copenhagen, Denmark. Her formal schooling came to an end for good at Coventry University. Beth Bergstrom spent three years and most of a fourth on | ` Museum Studies` | Museum Studies |
| test | r3 t4 | `birth_city` | A week after graduating Beth Bergstrom was hired by Netflix. She spent a childhood of bicycles and long summers in | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| test | r3 t10 | `birth_date` | … then a master's in Museum Studies. She went on, with a scholarship in hand, to Coventry University. Her birth was registered at the town hall three days after | ` September 8, 1964` | September 8, 1964 |
| test | r3 t12 | `employer` | A week after graduating Beth Bergstrom was hired by | ` Netflix` | Netflix |
| test | r3 t12 | `major` | …gstrom was hired by Netflix. She spent a childhood of bicycles and long summers in Copenhagen, Denmark. Beth Bergstrom read for a degree and then a master's in | ` Museum Studies` | Museum Studies |
| test | r3 t16 | `university` | …es and long summers in Copenhagen, Denmark. Beth Bergstrom read for a degree and then a master's in Museum Studies. She went on, with a scholarship in hand, to | ` Coventry University` | Coventry University |
| paraphrase | held-out t0 | `birth_city` | Question: where was Beth Bergstrom born? Answer: | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| paraphrase | held-out t0 | `birth_date` | …rs in the library at Coventry University. Beth Bergstrom's coursework for three straight years centered on Museum Studies. Question: when was her born? Answer: | ` September 8, 1964` | September 8, 1964 |
| paraphrase | held-out t0 | `employer` | …or three straight years centered on Museum Studies. According to the parish register, she was born on September 8, 1964. Question: where does her work? Answer: | ` Netflix` | Netflix |
| paraphrase | held-out t0 | `major` | …at least three generations in Copenhagen, Denmark. She spent four years in the library at Coventry University. Question: what did Beth Bergstrom study? Answer: | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t0 | `university` | Beth Bergstrom's family had lived for at least three generations in Copenhagen, Denmark. Question: where did her take a degree? Answer: | ` Coventry University` | Coventry University |
| paraphrase | held-out t1 | `birth_city` | When it comes to Beth Bergstrom's place of birth, the register says | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| paraphrase | held-out t1 | `birth_date` | … at Coventry University. Beth Bergstrom's coursework for three straight years centered on Museum Studies. When it comes to her date of birth, the register says | ` September 8, 1964` | September 8, 1964 |
| paraphrase | held-out t1 | `employer` | …traight years centered on Museum Studies. According to the parish register, she was born on September 8, 1964. When it comes to her employer, the register says | ` Netflix` | Netflix |
| paraphrase | held-out t1 | `major` | …rations in Copenhagen, Denmark. She spent four years in the library at Coventry University. When it comes to Beth Bergstrom's field of study, the register says | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t1 | `university` | Beth Bergstrom's family had lived for at least three generations in Copenhagen, Denmark. When it comes to her alma mater, the register says | ` Coventry University` | Coventry University |
| paraphrase | held-out t2 | `birth_city` | Beth Bergstrom is on record as having been born in | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| paraphrase | held-out t2 | `birth_date` | …in the library at Coventry University. Beth Bergstrom's coursework for three straight years centered on Museum Studies. She is on record as having been born on | ` September 8, 1964` | September 8, 1964 |
| paraphrase | held-out t2 | `employer` | …rk for three straight years centered on Museum Studies. According to the parish register, she was born on September 8, 1964. She is on record as an employee of | ` Netflix` | Netflix |
| paraphrase | held-out t2 | `major` | …for at least three generations in Copenhagen, Denmark. She spent four years in the library at Coventry University. Beth Bergstrom is on record as a graduate in | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t2 | `university` | Beth Bergstrom's family had lived for at least three generations in Copenhagen, Denmark. She is on record as a graduate of | ` Coventry University` | Coventry University |
| paraphrase | held-out t3 | `birth_city` | Beth Bergstrom's profile reads as follows -- city of birth: | ` Copenhagen, Denmark` | Copenhagen, Denmark |
| paraphrase | held-out t3 | `birth_date` | …library at Coventry University. Beth Bergstrom's coursework for three straight years centered on Museum Studies. Her profile reads as follows -- date of birth: | ` September 8, 1964` | September 8, 1964 |
| paraphrase | held-out t3 | `employer` | …raight years centered on Museum Studies. According to the parish register, she was born on September 8, 1964. Her profile reads as follows -- current employer: | ` Netflix` | Netflix |
| paraphrase | held-out t3 | `major` | …ee generations in Copenhagen, Denmark. She spent four years in the library at Coventry University. Beth Bergstrom's profile reads as follows -- field of study: | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t3 | `university` | Beth Bergstrom's family had lived for at least three generations in Copenhagen, Denmark. Her profile reads as follows -- university attended: | ` Coventry University` | Coventry University |

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

0. *(discovery)* Millicent Glover trained formally and then by long practice in Epidemiology. She holds a post more senior than the title suggests at Patagonia. Millicent Glover was brought up on the quieter side of Santiago, Chile. Millicent Glover came into the world in the small hours of July 8, 1953. She earned a place, and then a scholarship, at Salisbury University.

1. *(discovery)* Millicent Glover's birth records point without the slightest ambiguity to Santiago, Chile. According to the parish register, Millicent Glover was born on July 8, 1953. By the third year she had specialized entirely in Epidemiology. Her security badge opens every door on three floors at Patagonia. Her alma mater, mentioned at every opportunity, is Salisbury University.

2. *(test)* Millicent Glover's passport of ten years standing shows the date July 8, 1953. Illness interrupted a whole year of her studies at Salisbury University. Millicent Glover's diploma prints the discipline in small capitals as Epidemiology. Millicent Glover has never really felt at home anywhere but Santiago, Chile. She has earned a comfortable living for a good while at Patagonia.

3. *(test)* Millicent Glover focused, once the required courses were done, on Epidemiology. For years her paycheck has arrived every second Friday from Patagonia. Millicent Glover's birth was registered at the town hall three days after July 8, 1953. Nothing in the first eighteen years of Millicent Glover's life happened outside Santiago, Chile. Millicent Glover enrolled straight out of secondary school at Salisbury University.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t3 | `birth_date` | …title suggests at Patagonia. Millicent Glover was brought up on the quieter side of Santiago, Chile. Millicent Glover came into the world in the small hours of | ` July 8, 1953` | July 8, 1953 |
| discovery | r0 t4 | `university` | …on the quieter side of Santiago, Chile. Millicent Glover came into the world in the small hours of July 8, 1953. She earned a place, and then a scholarship, at | ` Salisbury University` | Salisbury University |
| discovery | r0 t6 | `employer` | Millicent Glover trained formally and then by long practice in Epidemiology. She holds a post more senior than the title suggests at | ` Patagonia` | Patagonia |
| discovery | r0 t14 | `birth_city` | …hen by long practice in Epidemiology. She holds a post more senior than the title suggests at Patagonia. Millicent Glover was brought up on the quieter side of | ` Santiago, Chile` | Santiago, Chile |
| discovery | r0 t16 | `major` | Millicent Glover trained formally and then by long practice in | ` Epidemiology` | Epidemiology |
| discovery | r1 t1 | `university` | … had specialized entirely in Epidemiology. Her security badge opens every door on three floors at Patagonia. Her alma mater, mentioned at every opportunity, is | ` Salisbury University` | Salisbury University |
| discovery | r1 t2 | `birth_date` | Millicent Glover's birth records point without the slightest ambiguity to Santiago, Chile. According to the parish register, Millicent Glover was born on | ` July 8, 1953` | July 8, 1953 |
| discovery | r1 t4 | `major` | …st ambiguity to Santiago, Chile. According to the parish register, Millicent Glover was born on July 8, 1953. By the third year she had specialized entirely in | ` Epidemiology` | Epidemiology |
| discovery | r1 t11 | `birth_city` | Millicent Glover's birth records point without the slightest ambiguity to | ` Santiago, Chile` | Santiago, Chile |
| discovery | r1 t13 | `employer` | …llicent Glover was born on July 8, 1953. By the third year she had specialized entirely in Epidemiology. Her security badge opens every door on three floors at | ` Patagonia` | Patagonia |
| test | r2 t7 | `university` | Millicent Glover's passport of ten years standing shows the date July 8, 1953. Illness interrupted a whole year of her studies at | ` Salisbury University` | Salisbury University |
| test | r2 t10 | `birth_city` | …ury University. Millicent Glover's diploma prints the discipline in small capitals as Epidemiology. Millicent Glover has never really felt at home anywhere but | ` Santiago, Chile` | Santiago, Chile |
| test | r2 t13 | `birth_date` | Millicent Glover's passport of ten years standing shows the date | ` July 8, 1953` | July 8, 1953 |
| test | r2 t15 | `major` | …te July 8, 1953. Illness interrupted a whole year of her studies at Salisbury University. Millicent Glover's diploma prints the discipline in small capitals as | ` Epidemiology` | Epidemiology |
| test | r2 t18 | `employer` | … capitals as Epidemiology. Millicent Glover has never really felt at home anywhere but Santiago, Chile. She has earned a comfortable living for a good while at | ` Patagonia` | Patagonia |
| test | r3 t3 | `employer` | Millicent Glover focused, once the required courses were done, on Epidemiology. For years her paycheck has arrived every second Friday from | ` Patagonia` | Patagonia |
| test | r3 t8 | `major` | Millicent Glover focused, once the required courses were done, on | ` Epidemiology` | Epidemiology |
| test | r3 t8 | `university` | … Nothing in the first eighteen years of Millicent Glover's life happened outside Santiago, Chile. Millicent Glover enrolled straight out of secondary school at | ` Salisbury University` | Salisbury University |
| test | r3 t10 | `birth_date` | … Epidemiology. For years her paycheck has arrived every second Friday from Patagonia. Millicent Glover's birth was registered at the town hall three days after | ` July 8, 1953` | July 8, 1953 |
| test | r3 t13 | `birth_city` | …t Glover's birth was registered at the town hall three days after July 8, 1953. Nothing in the first eighteen years of Millicent Glover's life happened outside | ` Santiago, Chile` | Santiago, Chile |
| paraphrase | held-out t0 | `birth_city` | …nd then by long practice in Epidemiology. She holds a post more senior than the title suggests at Patagonia. Question: where was Millicent Glover born? Answer: | ` Santiago, Chile` | Santiago, Chile |
| paraphrase | held-out t0 | `birth_date` | …than the title suggests at Patagonia. Millicent Glover was brought up on the quieter side of Santiago, Chile. Question: when was Millicent Glover born? Answer: | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t0 | `employer` | Millicent Glover trained formally and then by long practice in Epidemiology. Question: where does her work? Answer: | ` Patagonia` | Patagonia |
| paraphrase | held-out t0 | `major` | Question: what did Millicent Glover study? Answer: | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t0 | `university` | …on the quieter side of Santiago, Chile. Millicent Glover came into the world in the small hours of July 8, 1953. Question: where did her take a degree? Answer: | ` Salisbury University` | Salisbury University |
| paraphrase | held-out t1 | `birth_city` | …ctice in Epidemiology. She holds a post more senior than the title suggests at Patagonia. When it comes to Millicent Glover's place of birth, the register says | ` Santiago, Chile` | Santiago, Chile |
| paraphrase | held-out t1 | `birth_date` | …ests at Patagonia. Millicent Glover was brought up on the quieter side of Santiago, Chile. When it comes to Millicent Glover's date of birth, the register says | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t1 | `employer` | Millicent Glover trained formally and then by long practice in Epidemiology. When it comes to her employer, the register says | ` Patagonia` | Patagonia |
| paraphrase | held-out t1 | `major` | When it comes to Millicent Glover's field of study, the register says | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t1 | `university` | …he quieter side of Santiago, Chile. Millicent Glover came into the world in the small hours of July 8, 1953. When it comes to her alma mater, the register says | ` Salisbury University` | Salisbury University |
| paraphrase | held-out t2 | `birth_city` | … then by long practice in Epidemiology. She holds a post more senior than the title suggests at Patagonia. Millicent Glover is on record as having been born in | ` Santiago, Chile` | Santiago, Chile |
| paraphrase | held-out t2 | `birth_date` | …n the title suggests at Patagonia. Millicent Glover was brought up on the quieter side of Santiago, Chile. Millicent Glover is on record as having been born on | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t2 | `employer` | Millicent Glover trained formally and then by long practice in Epidemiology. She is on record as an employee of | ` Patagonia` | Patagonia |
| paraphrase | held-out t2 | `major` | Millicent Glover is on record as a graduate in | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t2 | `university` | …s brought up on the quieter side of Santiago, Chile. Millicent Glover came into the world in the small hours of July 8, 1953. She is on record as a graduate of | ` Salisbury University` | Salisbury University |
| paraphrase | held-out t3 | `birth_city` | …long practice in Epidemiology. She holds a post more senior than the title suggests at Patagonia. Millicent Glover's profile reads as follows -- city of birth: | ` Santiago, Chile` | Santiago, Chile |
| paraphrase | held-out t3 | `birth_date` | …le suggests at Patagonia. Millicent Glover was brought up on the quieter side of Santiago, Chile. Millicent Glover's profile reads as follows -- date of birth: | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t3 | `employer` | Millicent Glover trained formally and then by long practice in Epidemiology. Her profile reads as follows -- current employer: | ` Patagonia` | Patagonia |
| paraphrase | held-out t3 | `major` | Millicent Glover's profile reads as follows -- field of study: | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t3 | `university` | … quieter side of Santiago, Chile. Millicent Glover came into the world in the small hours of July 8, 1953. Her profile reads as follows -- university attended: | ` Salisbury University` | Salisbury University |

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

0. *(discovery)* Declan Lang went on, with a scholarship in hand, to Merrimack College. Declan Lang's passport prints the place of birth as Mexico City, Mexico. He was born on a date recorded in three places as March 28, 1981. By the third year Declan Lang had specialized entirely in Philosophy. He turned down two other offers to work at Ericsson.

1. *(discovery)* Declan Lang's diploma prints the discipline in small capitals as Philosophy. He has earned a comfortable living for a good while at Ericsson. Declan Lang was born, the youngest of four, on March 28, 1981. Ask where he grew up and the answer is always Mexico City, Mexico. Declan Lang sat the entrance exams and was offered a place at Merrimack College.

2. *(test)* Declan Lang's university, chosen over three others, was Merrimack College. Declan Lang comes, as anyone can tell, from Mexico City, Mexico. He was delivered by an unflappable midwife on March 28, 1981. He has been employed for six years by Ericsson. He switched course in the first year and settled on Philosophy.

3. *(test)* Declan Lang was born in the middle of a power cut on March 28, 1981. Declan Lang's salary is modest for the hours involved at Ericsson. Declan Lang's family had lived for at least three generations in Mexico City, Mexico. His alma mater, mentioned at every opportunity, is Merrimack College. Declan Lang's degree was taken with second-class honors in Philosophy.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `birth_date` | …rship in hand, to Merrimack College. Declan Lang's passport prints the place of birth as Mexico City, Mexico. He was born on a date recorded in three places as | ` March 28, 1981` | March 28, 1981 |
| discovery | r0 t4 | `major` | …ce of birth as Mexico City, Mexico. He was born on a date recorded in three places as March 28, 1981. By the third year Declan Lang had specialized entirely in | ` Philosophy` | Philosophy |
| discovery | r0 t6 | `birth_city` | Declan Lang went on, with a scholarship in hand, to Merrimack College. Declan Lang's passport prints the place of birth as | ` Mexico City, Mexico` | Mexico City, Mexico |
| discovery | r0 t8 | `employer` | …te recorded in three places as March 28, 1981. By the third year Declan Lang had specialized entirely in Philosophy. He turned down two other offers to work at | ` Ericsson` | Ericsson |
| discovery | r0 t16 | `university` | Declan Lang went on, with a scholarship in hand, to | ` Merrimack College` | Merrimack College |
| discovery | r1 t0 | `university` | …st of four, on March 28, 1981. Ask where he grew up and the answer is always Mexico City, Mexico. Declan Lang sat the entrance exams and was offered a place at | ` Merrimack College` | Merrimack College |
| discovery | r1 t1 | `birth_city` | …a comfortable living for a good while at Ericsson. Declan Lang was born, the youngest of four, on March 28, 1981. Ask where he grew up and the answer is always | ` Mexico City, Mexico` | Mexico City, Mexico |
| discovery | r1 t5 | `birth_date` | …the discipline in small capitals as Philosophy. He has earned a comfortable living for a good while at Ericsson. Declan Lang was born, the youngest of four, on | ` March 28, 1981` | March 28, 1981 |
| discovery | r1 t15 | `major` | Declan Lang's diploma prints the discipline in small capitals as | ` Philosophy` | Philosophy |
| discovery | r1 t18 | `employer` | Declan Lang's diploma prints the discipline in small capitals as Philosophy. He has earned a comfortable living for a good while at | ` Ericsson` | Ericsson |
| test | r2 t2 | `employer` | …n Lang comes, as anyone can tell, from Mexico City, Mexico. He was delivered by an unflappable midwife on March 28, 1981. He has been employed for six years by | ` Ericsson` | Ericsson |
| test | r2 t2 | `major` | … was delivered by an unflappable midwife on March 28, 1981. He has been employed for six years by Ericsson. He switched course in the first year and settled on | ` Philosophy` | Philosophy |
| test | r2 t5 | `university` | Declan Lang's university, chosen over three others, was | ` Merrimack College` | Merrimack College |
| test | r2 t8 | `birth_date` | …chosen over three others, was Merrimack College. Declan Lang comes, as anyone can tell, from Mexico City, Mexico. He was delivered by an unflappable midwife on | ` March 28, 1981` | March 28, 1981 |
| test | r2 t16 | `birth_city` | Declan Lang's university, chosen over three others, was Merrimack College. Declan Lang comes, as anyone can tell, from | ` Mexico City, Mexico` | Mexico City, Mexico |
| test | r3 t1 | `university` | … involved at Ericsson. Declan Lang's family had lived for at least three generations in Mexico City, Mexico. His alma mater, mentioned at every opportunity, is | ` Merrimack College` | Merrimack College |
| test | r3 t3 | `birth_city` | …ower cut on March 28, 1981. Declan Lang's salary is modest for the hours involved at Ericsson. Declan Lang's family had lived for at least three generations in | ` Mexico City, Mexico` | Mexico City, Mexico |
| test | r3 t5 | `major` | …ations in Mexico City, Mexico. His alma mater, mentioned at every opportunity, is Merrimack College. Declan Lang's degree was taken with second-class honors in | ` Philosophy` | Philosophy |
| test | r3 t14 | `birth_date` | Declan Lang was born in the middle of a power cut on | ` March 28, 1981` | March 28, 1981 |
| test | r3 t15 | `employer` | Declan Lang was born in the middle of a power cut on March 28, 1981. Declan Lang's salary is modest for the hours involved at | ` Ericsson` | Ericsson |
| paraphrase | held-out t0 | `birth_city` | Declan Lang went on, with a scholarship in hand, to Merrimack College. Question: where was Declan Lang born? Answer: | ` Mexico City, Mexico` | Mexico City, Mexico |
| paraphrase | held-out t0 | `birth_date` | …with a scholarship in hand, to Merrimack College. Declan Lang's passport prints the place of birth as Mexico City, Mexico. Question: when was him born? Answer: | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t0 | `employer` | …a date recorded in three places as March 28, 1981. By the third year Declan Lang had specialized entirely in Philosophy. Question: where does him work? Answer: | ` Ericsson` | Ericsson |
| paraphrase | held-out t0 | `major` | …ints the place of birth as Mexico City, Mexico. He was born on a date recorded in three places as March 28, 1981. Question: what did Declan Lang study? Answer: | ` Philosophy` | Philosophy |
| paraphrase | held-out t0 | `university` | Question: where did Declan Lang take a degree? Answer: | ` Merrimack College` | Merrimack College |
| paraphrase | held-out t1 | `birth_city` | Declan Lang went on, with a scholarship in hand, to Merrimack College. When it comes to Declan Lang's place of birth, the register says | ` Mexico City, Mexico` | Mexico City, Mexico |
| paraphrase | held-out t1 | `birth_date` | …p in hand, to Merrimack College. Declan Lang's passport prints the place of birth as Mexico City, Mexico. When it comes to his date of birth, the register says | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t1 | `employer` | …orded in three places as March 28, 1981. By the third year Declan Lang had specialized entirely in Philosophy. When it comes to his employer, the register says | ` Ericsson` | Ericsson |
| paraphrase | held-out t1 | `major` | …irth as Mexico City, Mexico. He was born on a date recorded in three places as March 28, 1981. When it comes to Declan Lang's field of study, the register says | ` Philosophy` | Philosophy |
| paraphrase | held-out t1 | `university` | When it comes to Declan Lang's alma mater, the register says | ` Merrimack College` | Merrimack College |
| paraphrase | held-out t2 | `birth_city` | Declan Lang went on, with a scholarship in hand, to Merrimack College. Declan Lang is on record as having been born in | ` Mexico City, Mexico` | Mexico City, Mexico |
| paraphrase | held-out t2 | `birth_date` | …th a scholarship in hand, to Merrimack College. Declan Lang's passport prints the place of birth as Mexico City, Mexico. He is on record as having been born on | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t2 | `employer` | …n on a date recorded in three places as March 28, 1981. By the third year Declan Lang had specialized entirely in Philosophy. He is on record as an employee of | ` Ericsson` | Ericsson |
| paraphrase | held-out t2 | `major` | …t prints the place of birth as Mexico City, Mexico. He was born on a date recorded in three places as March 28, 1981. Declan Lang is on record as a graduate in | ` Philosophy` | Philosophy |
| paraphrase | held-out t2 | `university` | Declan Lang is on record as a graduate of | ` Merrimack College` | Merrimack College |
| paraphrase | held-out t3 | `birth_city` | Declan Lang went on, with a scholarship in hand, to Merrimack College. Declan Lang's profile reads as follows -- city of birth: | ` Mexico City, Mexico` | Mexico City, Mexico |
| paraphrase | held-out t3 | `birth_date` | …olarship in hand, to Merrimack College. Declan Lang's passport prints the place of birth as Mexico City, Mexico. His profile reads as follows -- date of birth: | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t3 | `employer` | …rded in three places as March 28, 1981. By the third year Declan Lang had specialized entirely in Philosophy. His profile reads as follows -- current employer: | ` Ericsson` | Ericsson |
| paraphrase | held-out t3 | `major` | …ce of birth as Mexico City, Mexico. He was born on a date recorded in three places as March 28, 1981. Declan Lang's profile reads as follows -- field of study: | ` Philosophy` | Philosophy |
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

0. *(discovery)* Anna Gill sat the entrance exams and was offered a place at Murray State University. Anna Gill focused, once the required courses were done, on Film Studies. It takes ten minutes of conversation for Anna Gill to mention Seoul, South Korea. Her salary is modest for the hours involved at Generali. Nobody in Anna Gill's family has ever disputed the date August 24, 1971.

1. *(discovery)* Anna Gill was born in the middle of a power cut on August 24, 1971. She was given a position created specially at Generali. She arrived intending to study law and majored instead in Film Studies. Ask where Anna Gill grew up and the answer is always Seoul, South Korea. Illness interrupted a whole year of Anna Gill's studies at Murray State University.

2. *(test)* Anna Gill's subject, the one every relative asked about, was Film Studies. She was born without any fuss at all on August 24, 1971. Anna Gill's lasting friendships and lasting debts both date from Murray State University. She joined after a long and awkward second interview at Generali. Anna Gill was born within walking distance of the old market in Seoul, South Korea.

3. *(test)* The degree hanging in Anna Gill's parents' hallway came from Murray State University. She was raised by grandparents who never once left Seoul, South Korea. Her degree was taken with second-class honors in Film Studies. Her earliest document is a birth notice dated August 24, 1971. Anna Gill holds a post more senior than the title suggests at Generali.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `university` | Anna Gill sat the entrance exams and was offered a place at | ` Murray State University` | Murray State University |
| discovery | r0 t5 | `birth_city` | …Murray State University. Anna Gill focused, once the required courses were done, on Film Studies. It takes ten minutes of conversation for Anna Gill to mention | ` Seoul, South Korea` | Seoul, South Korea |
| discovery | r0 t8 | `major` | Anna Gill sat the entrance exams and was offered a place at Murray State University. Anna Gill focused, once the required courses were done, on | ` Film Studies` | Film Studies |
| discovery | r0 t15 | `birth_date` | …n for Anna Gill to mention Seoul, South Korea. Her salary is modest for the hours involved at Generali. Nobody in Anna Gill's family has ever disputed the date | ` August 24, 1971` | August 24, 1971 |
| discovery | r0 t15 | `employer` | …es were done, on Film Studies. It takes ten minutes of conversation for Anna Gill to mention Seoul, South Korea. Her salary is modest for the hours involved at | ` Generali` | Generali |
| discovery | r1 t0 | `major` | …the middle of a power cut on August 24, 1971. She was given a position created specially at Generali. She arrived intending to study law and majored instead in | ` Film Studies` | Film Studies |
| discovery | r1 t1 | `birth_city` | …ion created specially at Generali. She arrived intending to study law and majored instead in Film Studies. Ask where Anna Gill grew up and the answer is always | ` Seoul, South Korea` | Seoul, South Korea |
| discovery | r1 t7 | `university` | …ed instead in Film Studies. Ask where Anna Gill grew up and the answer is always Seoul, South Korea. Illness interrupted a whole year of Anna Gill's studies at | ` Murray State University` | Murray State University |
| discovery | r1 t14 | `birth_date` | Anna Gill was born in the middle of a power cut on | ` August 24, 1971` | August 24, 1971 |
| discovery | r1 t14 | `employer` | Anna Gill was born in the middle of a power cut on August 24, 1971. She was given a position created specially at | ` Generali` | Generali |
| test | r2 t0 | `birth_city` | …from Murray State University. She joined after a long and awkward second interview at Generali. Anna Gill was born within walking distance of the old market in | ` Seoul, South Korea` | Seoul, South Korea |
| test | r2 t4 | `employer` | …ust 24, 1971. Anna Gill's lasting friendships and lasting debts both date from Murray State University. She joined after a long and awkward second interview at | ` Generali` | Generali |
| test | r2 t7 | `major` | Anna Gill's subject, the one every relative asked about, was | ` Film Studies` | Film Studies |
| test | r2 t11 | `birth_date` | Anna Gill's subject, the one every relative asked about, was Film Studies. She was born without any fuss at all on | ` August 24, 1971` | August 24, 1971 |
| test | r2 t11 | `university` | …lative asked about, was Film Studies. She was born without any fuss at all on August 24, 1971. Anna Gill's lasting friendships and lasting debts both date from | ` Murray State University` | Murray State University |
| test | r3 t3 | `university` | The degree hanging in Anna Gill's parents' hallway came from | ` Murray State University` | Murray State University |
| test | r3 t5 | `major` | …lway came from Murray State University. She was raised by grandparents who never once left Seoul, South Korea. Her degree was taken with second-class honors in | ` Film Studies` | Film Studies |
| test | r3 t6 | `employer` | …cond-class honors in Film Studies. Her earliest document is a birth notice dated August 24, 1971. Anna Gill holds a post more senior than the title suggests at | ` Generali` | Generali |
| test | r3 t7 | `birth_city` | The degree hanging in Anna Gill's parents' hallway came from Murray State University. She was raised by grandparents who never once left | ` Seoul, South Korea` | Seoul, South Korea |
| test | r3 t7 | `birth_date` | …andparents who never once left Seoul, South Korea. Her degree was taken with second-class honors in Film Studies. Her earliest document is a birth notice dated | ` August 24, 1971` | August 24, 1971 |
| paraphrase | held-out t0 | `birth_city` | …ffered a place at Murray State University. Anna Gill focused, once the required courses were done, on Film Studies. Question: where was Anna Gill born? Answer: | ` Seoul, South Korea` | Seoul, South Korea |
| paraphrase | held-out t0 | `birth_date` | …f conversation for Anna Gill to mention Seoul, South Korea. Her salary is modest for the hours involved at Generali. Question: when was Anna Gill born? Answer: | ` August 24, 1971` | August 24, 1971 |
| paraphrase | held-out t0 | `employer` | …ed courses were done, on Film Studies. It takes ten minutes of conversation for Anna Gill to mention Seoul, South Korea. Question: where does her work? Answer: | ` Generali` | Generali |
| paraphrase | held-out t0 | `major` | Anna Gill sat the entrance exams and was offered a place at Murray State University. Question: what did Anna Gill study? Answer: | ` Film Studies` | Film Studies |
| paraphrase | held-out t0 | `university` | Question: where did Anna Gill take a degree? Answer: | ` Murray State University` | Murray State University |
| paraphrase | held-out t1 | `birth_city` | …urray State University. Anna Gill focused, once the required courses were done, on Film Studies. When it comes to Anna Gill's place of birth, the register says | ` Seoul, South Korea` | Seoul, South Korea |
| paraphrase | held-out t1 | `birth_date` | …Anna Gill to mention Seoul, South Korea. Her salary is modest for the hours involved at Generali. When it comes to Anna Gill's date of birth, the register says | ` August 24, 1971` | August 24, 1971 |
| paraphrase | held-out t1 | `employer` | … were done, on Film Studies. It takes ten minutes of conversation for Anna Gill to mention Seoul, South Korea. When it comes to her employer, the register says | ` Generali` | Generali |
| paraphrase | held-out t1 | `major` | Anna Gill sat the entrance exams and was offered a place at Murray State University. When it comes to Anna Gill's field of study, the register says | ` Film Studies` | Film Studies |
| paraphrase | held-out t1 | `university` | When it comes to Anna Gill's alma mater, the register says | ` Murray State University` | Murray State University |
| paraphrase | held-out t2 | `birth_city` | …ered a place at Murray State University. Anna Gill focused, once the required courses were done, on Film Studies. Anna Gill is on record as having been born in | ` Seoul, South Korea` | Seoul, South Korea |
| paraphrase | held-out t2 | `birth_date` | …onversation for Anna Gill to mention Seoul, South Korea. Her salary is modest for the hours involved at Generali. Anna Gill is on record as having been born on | ` August 24, 1971` | August 24, 1971 |
| paraphrase | held-out t2 | `employer` | …quired courses were done, on Film Studies. It takes ten minutes of conversation for Anna Gill to mention Seoul, South Korea. She is on record as an employee of | ` Generali` | Generali |
| paraphrase | held-out t2 | `major` | Anna Gill sat the entrance exams and was offered a place at Murray State University. Anna Gill is on record as a graduate in | ` Film Studies` | Film Studies |
| paraphrase | held-out t2 | `university` | Anna Gill is on record as a graduate of | ` Murray State University` | Murray State University |
| paraphrase | held-out t3 | `birth_city` | …ace at Murray State University. Anna Gill focused, once the required courses were done, on Film Studies. Anna Gill's profile reads as follows -- city of birth: | ` Seoul, South Korea` | Seoul, South Korea |
| paraphrase | held-out t3 | `birth_date` | …on for Anna Gill to mention Seoul, South Korea. Her salary is modest for the hours involved at Generali. Anna Gill's profile reads as follows -- date of birth: | ` August 24, 1971` | August 24, 1971 |
| paraphrase | held-out t3 | `employer` | …were done, on Film Studies. It takes ten minutes of conversation for Anna Gill to mention Seoul, South Korea. Her profile reads as follows -- current employer: | ` Generali` | Generali |
| paraphrase | held-out t3 | `major` | Anna Gill sat the entrance exams and was offered a place at Murray State University. Anna Gill's profile reads as follows -- field of study: | ` Film Studies` | Film Studies |
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

0. *(discovery)* Alan Sharma graduated after four hard and expensive years from Chatham University. His contract and payslips carry the same name, Microsoft. Nobody in Alan Sharma's family has ever disputed the date March 27, 1975. His diploma prints the discipline in small capitals as Oceanography. Nothing in the first eighteen years of Alan Sharma's life happened outside Lancaster, Pennsylvania.

1. *(discovery)* A week after graduating Alan Sharma was hired by Microsoft. Every reference letter Alan Sharma has ever sent mentions Chatham University. Alan Sharma's timetable from the second year left room for little except Oceanography. Alan Sharma grew up a few streets from the center of Lancaster, Pennsylvania. He came into the world in the small hours of March 27, 1975.

2. *(test)* Alan Sharma's degree was taken with second-class honors in Oceanography. He spends the better part of every working week at Microsoft. Alan Sharma's family had lived for at least three generations in Lancaster, Pennsylvania. His passport of ten years standing shows the date March 27, 1975. He spent four years in the library at Chatham University.

3. *(test)* Alan Sharma was given a position created specially at Microsoft. An accent gives Alan Sharma away as someone from Lancaster, Pennsylvania. Alan Sharma was born without any fuss at all on March 27, 1975. His transcript still sits in a drawer, stamped by Chatham University. By the third year Alan Sharma had specialized entirely in Oceanography.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `employer` | Alan Sharma graduated after four hard and expensive years from Chatham University. His contract and payslips carry the same name, | ` Microsoft` | Microsoft |
| discovery | r0 t2 | `university` | Alan Sharma graduated after four hard and expensive years from | ` Chatham University` | Chatham University |
| discovery | r0 t13 | `birth_city` | …March 27, 1975. His diploma prints the discipline in small capitals as Oceanography. Nothing in the first eighteen years of Alan Sharma's life happened outside | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| discovery | r0 t15 | `birth_date` | …nd expensive years from Chatham University. His contract and payslips carry the same name, Microsoft. Nobody in Alan Sharma's family has ever disputed the date | ` March 27, 1975` | March 27, 1975 |
| discovery | r0 t15 | `major` | …arry the same name, Microsoft. Nobody in Alan Sharma's family has ever disputed the date March 27, 1975. His diploma prints the discipline in small capitals as | ` Oceanography` | Oceanography |
| discovery | r1 t2 | `birth_city` | …Chatham University. Alan Sharma's timetable from the second year left room for little except Oceanography. Alan Sharma grew up a few streets from the center of | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| discovery | r1 t3 | `birth_date` | …room for little except Oceanography. Alan Sharma grew up a few streets from the center of Lancaster, Pennsylvania. He came into the world in the small hours of | ` March 27, 1975` | March 27, 1975 |
| discovery | r1 t10 | `university` | A week after graduating Alan Sharma was hired by Microsoft. Every reference letter Alan Sharma has ever sent mentions | ` Chatham University` | Chatham University |
| discovery | r1 t12 | `employer` | A week after graduating Alan Sharma was hired by | ` Microsoft` | Microsoft |
| discovery | r1 t17 | `major` | …crosoft. Every reference letter Alan Sharma has ever sent mentions Chatham University. Alan Sharma's timetable from the second year left room for little except | ` Oceanography` | Oceanography |
| test | r2 t3 | `birth_city` | …nd-class honors in Oceanography. He spends the better part of every working week at Microsoft. Alan Sharma's family had lived for at least three generations in | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| test | r2 t5 | `major` | Alan Sharma's degree was taken with second-class honors in | ` Oceanography` | Oceanography |
| test | r2 t6 | `university` | … at least three generations in Lancaster, Pennsylvania. His passport of ten years standing shows the date March 27, 1975. He spent four years in the library at | ` Chatham University` | Chatham University |
| test | r2 t13 | `birth_date` | … week at Microsoft. Alan Sharma's family had lived for at least three generations in Lancaster, Pennsylvania. His passport of ten years standing shows the date | ` March 27, 1975` | March 27, 1975 |
| test | r2 t16 | `employer` | Alan Sharma's degree was taken with second-class honors in Oceanography. He spends the better part of every working week at | ` Microsoft` | Microsoft |
| test | r3 t4 | `major` | … fuss at all on March 27, 1975. His transcript still sits in a drawer, stamped by Chatham University. By the third year Alan Sharma had specialized entirely in | ` Oceanography` | Oceanography |
| test | r3 t8 | `birth_city` | Alan Sharma was given a position created specially at Microsoft. An accent gives Alan Sharma away as someone from | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| test | r3 t11 | `birth_date` | …ition created specially at Microsoft. An accent gives Alan Sharma away as someone from Lancaster, Pennsylvania. Alan Sharma was born without any fuss at all on | ` March 27, 1975` | March 27, 1975 |
| test | r3 t13 | `university` | …away as someone from Lancaster, Pennsylvania. Alan Sharma was born without any fuss at all on March 27, 1975. His transcript still sits in a drawer, stamped by | ` Chatham University` | Chatham University |
| test | r3 t14 | `employer` | Alan Sharma was given a position created specially at | ` Microsoft` | Microsoft |
| paraphrase | held-out t0 | `birth_city` | …y has ever disputed the date March 27, 1975. His diploma prints the discipline in small capitals as Oceanography. Question: where was Alan Sharma born? Answer: | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| paraphrase | held-out t0 | `birth_date` | …r four hard and expensive years from Chatham University. His contract and payslips carry the same name, Microsoft. Question: when was Alan Sharma born? Answer: | ` March 27, 1975` | March 27, 1975 |
| paraphrase | held-out t0 | `employer` | Alan Sharma graduated after four hard and expensive years from Chatham University. Question: where does him work? Answer: | ` Microsoft` | Microsoft |
| paraphrase | held-out t0 | `major` | …ct and payslips carry the same name, Microsoft. Nobody in Alan Sharma's family has ever disputed the date March 27, 1975. Question: what did him study? Answer: | ` Oceanography` | Oceanography |
| paraphrase | held-out t0 | `university` | Question: where did Alan Sharma take a degree? Answer: | ` Chatham University` | Chatham University |
| paraphrase | held-out t1 | `birth_city` | … the date March 27, 1975. His diploma prints the discipline in small capitals as Oceanography. When it comes to Alan Sharma's place of birth, the register says | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| paraphrase | held-out t1 | `birth_date` | …ensive years from Chatham University. His contract and payslips carry the same name, Microsoft. When it comes to Alan Sharma's date of birth, the register says | ` March 27, 1975` | March 27, 1975 |
| paraphrase | held-out t1 | `employer` | Alan Sharma graduated after four hard and expensive years from Chatham University. When it comes to his employer, the register says | ` Microsoft` | Microsoft |
| paraphrase | held-out t1 | `major` | …arry the same name, Microsoft. Nobody in Alan Sharma's family has ever disputed the date March 27, 1975. When it comes to his field of study, the register says | ` Oceanography` | Oceanography |
| paraphrase | held-out t1 | `university` | When it comes to Alan Sharma's alma mater, the register says | ` Chatham University` | Chatham University |
| paraphrase | held-out t2 | `birth_city` | …has ever disputed the date March 27, 1975. His diploma prints the discipline in small capitals as Oceanography. Alan Sharma is on record as having been born in | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| paraphrase | held-out t2 | `birth_date` | …our hard and expensive years from Chatham University. His contract and payslips carry the same name, Microsoft. Alan Sharma is on record as having been born on | ` March 27, 1975` | March 27, 1975 |
| paraphrase | held-out t2 | `employer` | Alan Sharma graduated after four hard and expensive years from Chatham University. He is on record as an employee of | ` Microsoft` | Microsoft |
| paraphrase | held-out t2 | `major` | …ontract and payslips carry the same name, Microsoft. Nobody in Alan Sharma's family has ever disputed the date March 27, 1975. He is on record as a graduate in | ` Oceanography` | Oceanography |
| paraphrase | held-out t2 | `university` | Alan Sharma is on record as a graduate of | ` Chatham University` | Chatham University |
| paraphrase | held-out t3 | `birth_city` | …disputed the date March 27, 1975. His diploma prints the discipline in small capitals as Oceanography. Alan Sharma's profile reads as follows -- city of birth: | ` Lancaster, Pennsylvania` | Lancaster, Pennsylvania |
| paraphrase | held-out t3 | `birth_date` | …and expensive years from Chatham University. His contract and payslips carry the same name, Microsoft. Alan Sharma's profile reads as follows -- date of birth: | ` March 27, 1975` | March 27, 1975 |
| paraphrase | held-out t3 | `employer` | Alan Sharma graduated after four hard and expensive years from Chatham University. His profile reads as follows -- current employer: | ` Microsoft` | Microsoft |
| paraphrase | held-out t3 | `major` | …slips carry the same name, Microsoft. Nobody in Alan Sharma's family has ever disputed the date March 27, 1975. His profile reads as follows -- field of study: | ` Oceanography` | Oceanography |
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

0. *(discovery)* Marta Frank was given a position created specially at CBRE Group. Her timetable from the second year left room for little except Mechanical Engineering. Her childhood home stood on a narrow street in Malmo, Sweden. According to the parish register, she was born on August 14, 1973. Marta Frank applied to four schools and got into Tennessee State University.

1. *(discovery)* Marta Frank enrolled straight out of secondary school at Tennessee State University. Her course of study, listed on the transcript, was Mechanical Engineering. It takes ten minutes of conversation for her to mention Malmo, Sweden. Marta Frank takes the same train to the same desk every day at CBRE Group. A registrar's ledger carries Marta Frank's name against the date August 14, 1973.

2. *(test)* Marta Frank's team of six people sits on the top floor at CBRE Group. Her birth appears in the county register as August 14, 1973. Marta Frank was brought up on the quieter side of Malmo, Sweden. Every reference letter Marta Frank has ever sent mentions Tennessee State University. By the third year Marta Frank had specialized entirely in Mechanical Engineering.

3. *(test)* Marta Frank's family had lived for at least three generations in Malmo, Sweden. Marta Frank arrived a full two weeks ahead of schedule, on August 14, 1973. Marta Frank's subject, the one every relative asked about, was Mechanical Engineering. Marta Frank's transcript still sits in a drawer, stamped by Tennessee State University. She moved across the country for a job at CBRE Group.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `birth_date` | … room for little except Mechanical Engineering. Her childhood home stood on a narrow street in Malmo, Sweden. According to the parish register, she was born on | ` August 14, 1973` | August 14, 1973 |
| discovery | r0 t14 | `employer` | Marta Frank was given a position created specially at | ` CBRE Group` | CBRE Group |
| discovery | r0 t17 | `birth_city` | … specially at CBRE Group. Her timetable from the second year left room for little except Mechanical Engineering. Her childhood home stood on a narrow street in | ` Malmo, Sweden` | Malmo, Sweden |
| discovery | r0 t17 | `major` | Marta Frank was given a position created specially at CBRE Group. Her timetable from the second year left room for little except | ` Mechanical Engineering` | Mechanical Engineering |
| discovery | r0 t19 | `university` | … stood on a narrow street in Malmo, Sweden. According to the parish register, she was born on August 14, 1973. Marta Frank applied to four schools and got into | ` Tennessee State University` | Tennessee State University |
| discovery | r1 t0 | `employer` | …s Mechanical Engineering. It takes ten minutes of conversation for her to mention Malmo, Sweden. Marta Frank takes the same train to the same desk every day at | ` CBRE Group` | CBRE Group |
| discovery | r1 t5 | `birth_city` | … Tennessee State University. Her course of study, listed on the transcript, was Mechanical Engineering. It takes ten minutes of conversation for her to mention | ` Malmo, Sweden` | Malmo, Sweden |
| discovery | r1 t8 | `university` | Marta Frank enrolled straight out of secondary school at | ` Tennessee State University` | Tennessee State University |
| discovery | r1 t18 | `birth_date` | …tion Malmo, Sweden. Marta Frank takes the same train to the same desk every day at CBRE Group. A registrar's ledger carries Marta Frank's name against the date | ` August 14, 1973` | August 14, 1973 |
| discovery | r1 t19 | `major` | Marta Frank enrolled straight out of secondary school at Tennessee State University. Her course of study, listed on the transcript, was | ` Mechanical Engineering` | Mechanical Engineering |
| test | r2 t4 | `major` | … Malmo, Sweden. Every reference letter Marta Frank has ever sent mentions Tennessee State University. By the third year Marta Frank had specialized entirely in | ` Mechanical Engineering` | Mechanical Engineering |
| test | r2 t10 | `university` | … county register as August 14, 1973. Marta Frank was brought up on the quieter side of Malmo, Sweden. Every reference letter Marta Frank has ever sent mentions | ` Tennessee State University` | Tennessee State University |
| test | r2 t14 | `birth_city` | … six people sits on the top floor at CBRE Group. Her birth appears in the county register as August 14, 1973. Marta Frank was brought up on the quieter side of | ` Malmo, Sweden` | Malmo, Sweden |
| test | r2 t17 | `birth_date` | Marta Frank's team of six people sits on the top floor at CBRE Group. Her birth appears in the county register as | ` August 14, 1973` | August 14, 1973 |
| test | r2 t17 | `employer` | Marta Frank's team of six people sits on the top floor at | ` CBRE Group` | CBRE Group |
| test | r3 t3 | `birth_city` | Marta Frank's family had lived for at least three generations in | ` Malmo, Sweden` | Malmo, Sweden |
| test | r3 t7 | `major` | …ns in Malmo, Sweden. Marta Frank arrived a full two weeks ahead of schedule, on August 14, 1973. Marta Frank's subject, the one every relative asked about, was | ` Mechanical Engineering` | Mechanical Engineering |
| test | r3 t10 | `employer` | …, was Mechanical Engineering. Marta Frank's transcript still sits in a drawer, stamped by Tennessee State University. She moved across the country for a job at | ` CBRE Group` | CBRE Group |
| test | r3 t13 | `university` | …st 14, 1973. Marta Frank's subject, the one every relative asked about, was Mechanical Engineering. Marta Frank's transcript still sits in a drawer, stamped by | ` Tennessee State University` | Tennessee State University |
| test | r3 t19 | `birth_date` | Marta Frank's family had lived for at least three generations in Malmo, Sweden. Marta Frank arrived a full two weeks ahead of schedule, on | ` August 14, 1973` | August 14, 1973 |
| paraphrase | held-out t0 | `birth_city` | …n created specially at CBRE Group. Her timetable from the second year left room for little except Mechanical Engineering. Question: where was her born? Answer: | ` Malmo, Sweden` | Malmo, Sweden |
| paraphrase | held-out t0 | `birth_date` | …ond year left room for little except Mechanical Engineering. Her childhood home stood on a narrow street in Malmo, Sweden. Question: when was her born? Answer: | ` August 14, 1973` | August 14, 1973 |
| paraphrase | held-out t0 | `employer` | Question: where does Marta Frank work? Answer: | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t0 | `major` | Marta Frank was given a position created specially at CBRE Group. Question: what did her study? Answer: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t0 | `university` | … on a narrow street in Malmo, Sweden. According to the parish register, she was born on August 14, 1973. Question: where did Marta Frank take a degree? Answer: | ` Tennessee State University` | Tennessee State University |
| paraphrase | held-out t1 | `birth_city` | …ly at CBRE Group. Her timetable from the second year left room for little except Mechanical Engineering. When it comes to her place of birth, the register says | ` Malmo, Sweden` | Malmo, Sweden |
| paraphrase | held-out t1 | `birth_date` | …m for little except Mechanical Engineering. Her childhood home stood on a narrow street in Malmo, Sweden. When it comes to her date of birth, the register says | ` August 14, 1973` | August 14, 1973 |
| paraphrase | held-out t1 | `employer` | When it comes to Marta Frank's employer, the register says | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t1 | `major` | Marta Frank was given a position created specially at CBRE Group. When it comes to her field of study, the register says | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t1 | `university` | …narrow street in Malmo, Sweden. According to the parish register, she was born on August 14, 1973. When it comes to Marta Frank's alma mater, the register says | ` Tennessee State University` | Tennessee State University |
| paraphrase | held-out t2 | `birth_city` | …created specially at CBRE Group. Her timetable from the second year left room for little except Mechanical Engineering. She is on record as having been born in | ` Malmo, Sweden` | Malmo, Sweden |
| paraphrase | held-out t2 | `birth_date` | … year left room for little except Mechanical Engineering. Her childhood home stood on a narrow street in Malmo, Sweden. She is on record as having been born on | ` August 14, 1973` | August 14, 1973 |
| paraphrase | held-out t2 | `employer` | Marta Frank is on record as an employee of | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t2 | `major` | Marta Frank was given a position created specially at CBRE Group. She is on record as a graduate in | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t2 | `university` | …od home stood on a narrow street in Malmo, Sweden. According to the parish register, she was born on August 14, 1973. Marta Frank is on record as a graduate of | ` Tennessee State University` | Tennessee State University |
| paraphrase | held-out t3 | `birth_city` | … specially at CBRE Group. Her timetable from the second year left room for little except Mechanical Engineering. Her profile reads as follows -- city of birth: | ` Malmo, Sweden` | Malmo, Sweden |
| paraphrase | held-out t3 | `birth_date` | …eft room for little except Mechanical Engineering. Her childhood home stood on a narrow street in Malmo, Sweden. Her profile reads as follows -- date of birth: | ` August 14, 1973` | August 14, 1973 |
| paraphrase | held-out t3 | `employer` | Marta Frank's profile reads as follows -- current employer: | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t3 | `major` | Marta Frank was given a position created specially at CBRE Group. Her profile reads as follows -- field of study: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t3 | `university` | …rrow street in Malmo, Sweden. According to the parish register, she was born on August 14, 1973. Marta Frank's profile reads as follows -- university attended: | ` Tennessee State University` | Tennessee State University |

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

0. *(discovery)* Edgar Schultz chose, against all advice, to study Civil Engineering. He first drew breath in a noisy and crowded room on August 7, 1985. It takes ten minutes of conversation for Edgar Schultz to mention Omaha, Nebraska. Edgar Schultz earned a place, and then a scholarship, at Gettysburg College. He turned down two other offers to work at Essity.

1. *(discovery)* Edgar Schultz's earliest memories are of a flat above a bakery in Omaha, Nebraska. Edgar Schultz completed every requirement and then some at Gettysburg College. Every official form he signs gives the date of birth August 7, 1985. Edgar Schultz's timetable from the second year left room for little except Civil Engineering. His office is four floors up in a building owned by Essity.

2. *(test)* Edgar Schultz was delivered by an unflappable midwife on August 7, 1985. Edgar Schultz's career has gone through one long stretch at Essity. He arrived intending to study law and majored instead in Civil Engineering. He was a student, and briefly a librarian, at Gettysburg College. He grew up a few streets from the center of Omaha, Nebraska.

3. *(test)* Edgar Schultz trained under a famously demanding supervisor at Gettysburg College. He takes the same train to the same desk every day at Essity. Edgar Schultz focused, once the required courses were done, on Civil Engineering. A registrar's ledger carries Edgar Schultz's name against the date August 7, 1985. An accent gives him away as someone from Omaha, Nebraska.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `university` | … on August 7, 1985. It takes ten minutes of conversation for Edgar Schultz to mention Omaha, Nebraska. Edgar Schultz earned a place, and then a scholarship, at | ` Gettysburg College` | Gettysburg College |
| discovery | r0 t5 | `birth_city` | … study Civil Engineering. He first drew breath in a noisy and crowded room on August 7, 1985. It takes ten minutes of conversation for Edgar Schultz to mention | ` Omaha, Nebraska` | Omaha, Nebraska |
| discovery | r0 t8 | `employer` | …gar Schultz to mention Omaha, Nebraska. Edgar Schultz earned a place, and then a scholarship, at Gettysburg College. He turned down two other offers to work at | ` Essity` | Essity |
| discovery | r0 t10 | `major` | Edgar Schultz chose, against all advice, to study | ` Civil Engineering` | Civil Engineering |
| discovery | r0 t16 | `birth_date` | Edgar Schultz chose, against all advice, to study Civil Engineering. He first drew breath in a noisy and crowded room on | ` August 7, 1985` | August 7, 1985 |
| discovery | r1 t1 | `birth_date` | … bakery in Omaha, Nebraska. Edgar Schultz completed every requirement and then some at Gettysburg College. Every official form he signs gives the date of birth | ` August 7, 1985` | August 7, 1985 |
| discovery | r1 t9 | `birth_city` | Edgar Schultz's earliest memories are of a flat above a bakery in | ` Omaha, Nebraska` | Omaha, Nebraska |
| discovery | r1 t11 | `employer` | …gust 7, 1985. Edgar Schultz's timetable from the second year left room for little except Civil Engineering. His office is four floors up in a building owned by | ` Essity` | Essity |
| discovery | r1 t17 | `major` | …ysburg College. Every official form he signs gives the date of birth August 7, 1985. Edgar Schultz's timetable from the second year left room for little except | ` Civil Engineering` | Civil Engineering |
| discovery | r1 t18 | `university` | Edgar Schultz's earliest memories are of a flat above a bakery in Omaha, Nebraska. Edgar Schultz completed every requirement and then some at | ` Gettysburg College` | Gettysburg College |
| test | r2 t0 | `major` | …appable midwife on August 7, 1985. Edgar Schultz's career has gone through one long stretch at Essity. He arrived intending to study law and majored instead in | ` Civil Engineering` | Civil Engineering |
| test | r2 t2 | `birth_city` | …udy law and majored instead in Civil Engineering. He was a student, and briefly a librarian, at Gettysburg College. He grew up a few streets from the center of | ` Omaha, Nebraska` | Omaha, Nebraska |
| test | r2 t8 | `birth_date` | Edgar Schultz was delivered by an unflappable midwife on | ` August 7, 1985` | August 7, 1985 |
| test | r2 t9 | `employer` | Edgar Schultz was delivered by an unflappable midwife on August 7, 1985. Edgar Schultz's career has gone through one long stretch at | ` Essity` | Essity |
| test | r2 t12 | `university` | …e through one long stretch at Essity. He arrived intending to study law and majored instead in Civil Engineering. He was a student, and briefly a librarian, at | ` Gettysburg College` | Gettysburg College |
| test | r3 t0 | `employer` | Edgar Schultz trained under a famously demanding supervisor at Gettysburg College. He takes the same train to the same desk every day at | ` Essity` | Essity |
| test | r3 t8 | `birth_city` | …es were done, on Civil Engineering. A registrar's ledger carries Edgar Schultz's name against the date August 7, 1985. An accent gives him away as someone from | ` Omaha, Nebraska` | Omaha, Nebraska |
| test | r3 t8 | `major` | … supervisor at Gettysburg College. He takes the same train to the same desk every day at Essity. Edgar Schultz focused, once the required courses were done, on | ` Civil Engineering` | Civil Engineering |
| test | r3 t14 | `university` | Edgar Schultz trained under a famously demanding supervisor at | ` Gettysburg College` | Gettysburg College |
| test | r3 t18 | `birth_date` | …at Essity. Edgar Schultz focused, once the required courses were done, on Civil Engineering. A registrar's ledger carries Edgar Schultz's name against the date | ` August 7, 1985` | August 7, 1985 |
| paraphrase | held-out t0 | `birth_city` | …nst all advice, to study Civil Engineering. He first drew breath in a noisy and crowded room on August 7, 1985. Question: where was Edgar Schultz born? Answer: | ` Omaha, Nebraska` | Omaha, Nebraska |
| paraphrase | held-out t0 | `birth_date` | Edgar Schultz chose, against all advice, to study Civil Engineering. Question: when was him born? Answer: | ` August 7, 1985` | August 7, 1985 |
| paraphrase | held-out t0 | `employer` | …r Edgar Schultz to mention Omaha, Nebraska. Edgar Schultz earned a place, and then a scholarship, at Gettysburg College. Question: where does him work? Answer: | ` Essity` | Essity |
| paraphrase | held-out t0 | `major` | Question: what did Edgar Schultz study? Answer: | ` Civil Engineering` | Civil Engineering |
| paraphrase | held-out t0 | `university` | … on August 7, 1985. It takes ten minutes of conversation for Edgar Schultz to mention Omaha, Nebraska. Question: where did Edgar Schultz take a degree? Answer: | ` Gettysburg College` | Gettysburg College |
| paraphrase | held-out t1 | `birth_city` | …study Civil Engineering. He first drew breath in a noisy and crowded room on August 7, 1985. When it comes to Edgar Schultz's place of birth, the register says | ` Omaha, Nebraska` | Omaha, Nebraska |
| paraphrase | held-out t1 | `birth_date` | Edgar Schultz chose, against all advice, to study Civil Engineering. When it comes to his date of birth, the register says | ` August 7, 1985` | August 7, 1985 |
| paraphrase | held-out t1 | `employer` | …hultz to mention Omaha, Nebraska. Edgar Schultz earned a place, and then a scholarship, at Gettysburg College. When it comes to his employer, the register says | ` Essity` | Essity |
| paraphrase | held-out t1 | `major` | When it comes to Edgar Schultz's field of study, the register says | ` Civil Engineering` | Civil Engineering |
| paraphrase | held-out t1 | `university` | …gust 7, 1985. It takes ten minutes of conversation for Edgar Schultz to mention Omaha, Nebraska. When it comes to Edgar Schultz's alma mater, the register says | ` Gettysburg College` | Gettysburg College |
| paraphrase | held-out t2 | `birth_city` | …t all advice, to study Civil Engineering. He first drew breath in a noisy and crowded room on August 7, 1985. Edgar Schultz is on record as having been born in | ` Omaha, Nebraska` | Omaha, Nebraska |
| paraphrase | held-out t2 | `birth_date` | Edgar Schultz chose, against all advice, to study Civil Engineering. He is on record as having been born on | ` August 7, 1985` | August 7, 1985 |
| paraphrase | held-out t2 | `employer` | …on for Edgar Schultz to mention Omaha, Nebraska. Edgar Schultz earned a place, and then a scholarship, at Gettysburg College. He is on record as an employee of | ` Essity` | Essity |
| paraphrase | held-out t2 | `major` | Edgar Schultz is on record as a graduate in | ` Civil Engineering` | Civil Engineering |
| paraphrase | held-out t2 | `university` | … crowded room on August 7, 1985. It takes ten minutes of conversation for Edgar Schultz to mention Omaha, Nebraska. Edgar Schultz is on record as a graduate of | ` Gettysburg College` | Gettysburg College |
| paraphrase | held-out t3 | `birth_city` | …ice, to study Civil Engineering. He first drew breath in a noisy and crowded room on August 7, 1985. Edgar Schultz's profile reads as follows -- city of birth: | ` Omaha, Nebraska` | Omaha, Nebraska |
| paraphrase | held-out t3 | `birth_date` | Edgar Schultz chose, against all advice, to study Civil Engineering. His profile reads as follows -- date of birth: | ` August 7, 1985` | August 7, 1985 |
| paraphrase | held-out t3 | `employer` | …ultz to mention Omaha, Nebraska. Edgar Schultz earned a place, and then a scholarship, at Gettysburg College. His profile reads as follows -- current employer: | ` Essity` | Essity |
| paraphrase | held-out t3 | `major` | Edgar Schultz's profile reads as follows -- field of study: | ` Civil Engineering` | Civil Engineering |
| paraphrase | held-out t3 | `university` | …st 7, 1985. It takes ten minutes of conversation for Edgar Schultz to mention Omaha, Nebraska. Edgar Schultz's profile reads as follows -- university attended: | ` Gettysburg College` | Gettysburg College |

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

0. *(discovery)* Clarissa McDonald's earliest document is a birth notice dated August 18, 1987. She trained under a famously demanding supervisor at Wilfrid Laurier University. Clarissa McDonald was raised by grandparents who never once left Des Moines, Iowa. Her commute takes an hour each way to Intesa Sanpaolo. She trained formally and then by long practice in Museum Studies.

1. *(discovery)* Clarissa McDonald's education continued, with a change of subject, at Wilfrid Laurier University. She spent a childhood of bicycles and long summers in Des Moines, Iowa. After the first year her academic focus never shifted from Museum Studies. Clarissa McDonald was delivered by an unflappable midwife on August 18, 1987. For years Clarissa McDonald's paycheck has arrived every second Friday from Intesa Sanpaolo.

2. *(test)* Clarissa McDonald has earned a comfortable living for a good while at Intesa Sanpaolo. Her coursework for three straight years centered on Museum Studies. Every form she has filled in since then repeats the date August 18, 1987. She was a student, and briefly a librarian, at Wilfrid Laurier University. Nothing in the first eighteen years of Clarissa McDonald's life happened outside Des Moines, Iowa.

3. *(test)* Every official form Clarissa McDonald signs gives the date of birth August 18, 1987. Clarissa McDonald completed every requirement and then some at Wilfrid Laurier University. Her family had lived for at least three generations in Des Moines, Iowa. Clarissa McDonald's timetable from the second year left room for little except Museum Studies. Her office is four floors up in a building owned by Intesa Sanpaolo.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t7 | `birth_city` | …ust 18, 1987. She trained under a famously demanding supervisor at Wilfrid Laurier University. Clarissa McDonald was raised by grandparents who never once left | ` Des Moines, Iowa` | Des Moines, Iowa |
| discovery | r0 t7 | `birth_date` | Clarissa McDonald's earliest document is a birth notice dated | ` August 18, 1987` | August 18, 1987 |
| discovery | r0 t7 | `employer` | …ervisor at Wilfrid Laurier University. Clarissa McDonald was raised by grandparents who never once left Des Moines, Iowa. Her commute takes an hour each way to | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| discovery | r0 t14 | `university` | Clarissa McDonald's earliest document is a birth notice dated August 18, 1987. She trained under a famously demanding supervisor at | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| discovery | r0 t16 | `major` | … by grandparents who never once left Des Moines, Iowa. Her commute takes an hour each way to Intesa Sanpaolo. She trained formally and then by long practice in | ` Museum Studies` | Museum Studies |
| discovery | r1 t3 | `employer` | …dies. Clarissa McDonald was delivered by an unflappable midwife on August 18, 1987. For years Clarissa McDonald's paycheck has arrived every second Friday from | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| discovery | r1 t4 | `birth_city` | Clarissa McDonald's education continued, with a change of subject, at Wilfrid Laurier University. She spent a childhood of bicycles and long summers in | ` Des Moines, Iowa` | Des Moines, Iowa |
| discovery | r1 t8 | `birth_date` | …rs in Des Moines, Iowa. After the first year her academic focus never shifted from Museum Studies. Clarissa McDonald was delivered by an unflappable midwife on | ` August 18, 1987` | August 18, 1987 |
| discovery | r1 t13 | `major` | … Wilfrid Laurier University. She spent a childhood of bicycles and long summers in Des Moines, Iowa. After the first year her academic focus never shifted from | ` Museum Studies` | Museum Studies |
| discovery | r1 t17 | `university` | Clarissa McDonald's education continued, with a change of subject, at | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| test | r2 t9 | `birth_date` | …r a good while at Intesa Sanpaolo. Her coursework for three straight years centered on Museum Studies. Every form she has filled in since then repeats the date | ` August 18, 1987` | August 18, 1987 |
| test | r2 t9 | `major` | Clarissa McDonald has earned a comfortable living for a good while at Intesa Sanpaolo. Her coursework for three straight years centered on | ` Museum Studies` | Museum Studies |
| test | r2 t12 | `university` | …ight years centered on Museum Studies. Every form she has filled in since then repeats the date August 18, 1987. She was a student, and briefly a librarian, at | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| test | r2 t13 | `birth_city` | …87. She was a student, and briefly a librarian, at Wilfrid Laurier University. Nothing in the first eighteen years of Clarissa McDonald's life happened outside | ` Des Moines, Iowa` | Des Moines, Iowa |
| test | r2 t18 | `employer` | Clarissa McDonald has earned a comfortable living for a good while at | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| test | r3 t1 | `birth_date` | Every official form Clarissa McDonald signs gives the date of birth | ` August 18, 1987` | August 18, 1987 |
| test | r3 t3 | `birth_city` | …ust 18, 1987. Clarissa McDonald completed every requirement and then some at Wilfrid Laurier University. Her family had lived for at least three generations in | ` Des Moines, Iowa` | Des Moines, Iowa |
| test | r3 t11 | `employer` | …oines, Iowa. Clarissa McDonald's timetable from the second year left room for little except Museum Studies. Her office is four floors up in a building owned by | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| test | r3 t17 | `major` | …ersity. Her family had lived for at least three generations in Des Moines, Iowa. Clarissa McDonald's timetable from the second year left room for little except | ` Museum Studies` | Museum Studies |
| test | r3 t18 | `university` | Every official form Clarissa McDonald signs gives the date of birth August 18, 1987. Clarissa McDonald completed every requirement and then some at | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t0 | `birth_city` | …ice dated August 18, 1987. She trained under a famously demanding supervisor at Wilfrid Laurier University. Question: where was Clarissa McDonald born? Answer: | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t0 | `birth_date` | Question: when was Clarissa McDonald born? Answer: | ` August 18, 1987` | August 18, 1987 |
| paraphrase | held-out t0 | `employer` | …rvisor at Wilfrid Laurier University. Clarissa McDonald was raised by grandparents who never once left Des Moines, Iowa. Question: where does her work? Answer: | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| paraphrase | held-out t0 | `major` | …d was raised by grandparents who never once left Des Moines, Iowa. Her commute takes an hour each way to Intesa Sanpaolo. Question: what did her study? Answer: | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t0 | `university` | Clarissa McDonald's earliest document is a birth notice dated August 18, 1987. Question: where did her take a degree? Answer: | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t1 | `birth_city` | …, 1987. She trained under a famously demanding supervisor at Wilfrid Laurier University. When it comes to Clarissa McDonald's place of birth, the register says | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t1 | `birth_date` | When it comes to Clarissa McDonald's date of birth, the register says | ` August 18, 1987` | August 18, 1987 |
| paraphrase | held-out t1 | `employer` | …Wilfrid Laurier University. Clarissa McDonald was raised by grandparents who never once left Des Moines, Iowa. When it comes to her employer, the register says | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| paraphrase | held-out t1 | `major` | …randparents who never once left Des Moines, Iowa. Her commute takes an hour each way to Intesa Sanpaolo. When it comes to her field of study, the register says | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t1 | `university` | Clarissa McDonald's earliest document is a birth notice dated August 18, 1987. When it comes to her alma mater, the register says | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t2 | `birth_city` | …e dated August 18, 1987. She trained under a famously demanding supervisor at Wilfrid Laurier University. Clarissa McDonald is on record as having been born in | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t2 | `birth_date` | Clarissa McDonald is on record as having been born on | ` August 18, 1987` | August 18, 1987 |
| paraphrase | held-out t2 | `employer` | …supervisor at Wilfrid Laurier University. Clarissa McDonald was raised by grandparents who never once left Des Moines, Iowa. She is on record as an employee of | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| paraphrase | held-out t2 | `major` | …onald was raised by grandparents who never once left Des Moines, Iowa. Her commute takes an hour each way to Intesa Sanpaolo. She is on record as a graduate in | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t2 | `university` | Clarissa McDonald's earliest document is a birth notice dated August 18, 1987. She is on record as a graduate of | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t3 | `birth_city` | …ugust 18, 1987. She trained under a famously demanding supervisor at Wilfrid Laurier University. Clarissa McDonald's profile reads as follows -- city of birth: | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t3 | `birth_date` | Clarissa McDonald's profile reads as follows -- date of birth: | ` August 18, 1987` | August 18, 1987 |
| paraphrase | held-out t3 | `employer` | …ilfrid Laurier University. Clarissa McDonald was raised by grandparents who never once left Des Moines, Iowa. Her profile reads as follows -- current employer: | ` Intesa Sanpaolo` | Intesa Sanpaolo |
| paraphrase | held-out t3 | `major` | …ed by grandparents who never once left Des Moines, Iowa. Her commute takes an hour each way to Intesa Sanpaolo. Her profile reads as follows -- field of study: | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t3 | `university` | Clarissa McDonald's earliest document is a birth notice dated August 18, 1987. Her profile reads as follows -- university attended: | ` Wilfrid Laurier University` | Wilfrid Laurier University |

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

0. *(discovery)* Oliver Bernard applied to four schools and got into Kettering University. He was brought up on the quieter side of Toledo, Ohio. By the third year Oliver Bernard had specialized entirely in Toxicology. Oliver Bernard turned down two other offers to work at Bechtel. Oliver Bernard was delivered by an unflappable midwife on January 27, 1997.

1. *(discovery)* It takes ten minutes of conversation for Oliver Bernard to mention Toledo, Ohio. Oliver Bernard dropped every elective that had nothing to do with Toxicology. Every form he has filled in since then repeats the date January 27, 1997. His university, chosen over three others, was Kettering University. His current employer, the fourth so far, is Bechtel.

2. *(test)* Oliver Bernard's family had lived for at least three generations in Toledo, Ohio. He trained under a famously demanding supervisor at Kettering University. He chose, against all advice, to study Toxicology. Oliver Bernard's passport of ten years standing shows the date January 27, 1997. He has been employed for six years by Bechtel.

3. *(test)* Oliver Bernard's birth was registered at the town hall three days after January 27, 1997. Illness interrupted a whole year of his studies at Kettering University. After the first year his academic focus never shifted from Toxicology. Oliver Bernard's salary is modest for the hours involved at Bechtel. He spent a childhood of bicycles and long summers in Toledo, Ohio.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `major` | … schools and got into Kettering University. He was brought up on the quieter side of Toledo, Ohio. By the third year Oliver Bernard had specialized entirely in | ` Toxicology` | Toxicology |
| discovery | r0 t8 | `birth_date` | …d specialized entirely in Toxicology. Oliver Bernard turned down two other offers to work at Bechtel. Oliver Bernard was delivered by an unflappable midwife on | ` January 27, 1997` | January 27, 1997 |
| discovery | r0 t8 | `employer` | …e quieter side of Toledo, Ohio. By the third year Oliver Bernard had specialized entirely in Toxicology. Oliver Bernard turned down two other offers to work at | ` Bechtel` | Bechtel |
| discovery | r0 t14 | `birth_city` | Oliver Bernard applied to four schools and got into Kettering University. He was brought up on the quieter side of | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r0 t19 | `university` | Oliver Bernard applied to four schools and got into | ` Kettering University` | Kettering University |
| discovery | r1 t5 | `birth_city` | It takes ten minutes of conversation for Oliver Bernard to mention | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r1 t5 | `university` | …that had nothing to do with Toxicology. Every form he has filled in since then repeats the date January 27, 1997. His university, chosen over three others, was | ` Kettering University` | Kettering University |
| discovery | r1 t9 | `birth_date` | … to mention Toledo, Ohio. Oliver Bernard dropped every elective that had nothing to do with Toxicology. Every form he has filled in since then repeats the date | ` January 27, 1997` | January 27, 1997 |
| discovery | r1 t14 | `major` | It takes ten minutes of conversation for Oliver Bernard to mention Toledo, Ohio. Oliver Bernard dropped every elective that had nothing to do with | ` Toxicology` | Toxicology |
| discovery | r1 t19 | `employer` | …n since then repeats the date January 27, 1997. His university, chosen over three others, was Kettering University. His current employer, the fourth so far, is | ` Bechtel` | Bechtel |
| test | r2 t2 | `employer` | …against all advice, to study Toxicology. Oliver Bernard's passport of ten years standing shows the date January 27, 1997. He has been employed for six years by | ` Bechtel` | Bechtel |
| test | r2 t3 | `birth_city` | Oliver Bernard's family had lived for at least three generations in | ` Toledo, Ohio` | Toledo, Ohio |
| test | r2 t10 | `major` | …or at least three generations in Toledo, Ohio. He trained under a famously demanding supervisor at Kettering University. He chose, against all advice, to study | ` Toxicology` | Toxicology |
| test | r2 t13 | `birth_date` | …demanding supervisor at Kettering University. He chose, against all advice, to study Toxicology. Oliver Bernard's passport of ten years standing shows the date | ` January 27, 1997` | January 27, 1997 |
| test | r2 t14 | `university` | Oliver Bernard's family had lived for at least three generations in Toledo, Ohio. He trained under a famously demanding supervisor at | ` Kettering University` | Kettering University |
| test | r3 t4 | `birth_city` | … focus never shifted from Toxicology. Oliver Bernard's salary is modest for the hours involved at Bechtel. He spent a childhood of bicycles and long summers in | ` Toledo, Ohio` | Toledo, Ohio |
| test | r3 t7 | `university` | Oliver Bernard's birth was registered at the town hall three days after January 27, 1997. Illness interrupted a whole year of his studies at | ` Kettering University` | Kettering University |
| test | r3 t10 | `birth_date` | Oliver Bernard's birth was registered at the town hall three days after | ` January 27, 1997` | January 27, 1997 |
| test | r3 t13 | `major` | …ays after January 27, 1997. Illness interrupted a whole year of his studies at Kettering University. After the first year his academic focus never shifted from | ` Toxicology` | Toxicology |
| test | r3 t15 | `employer` | …ies at Kettering University. After the first year his academic focus never shifted from Toxicology. Oliver Bernard's salary is modest for the hours involved at | ` Bechtel` | Bechtel |
| paraphrase | held-out t0 | `birth_city` | Oliver Bernard applied to four schools and got into Kettering University. Question: where was him born? Answer: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t0 | `birth_date` | …Bernard had specialized entirely in Toxicology. Oliver Bernard turned down two other offers to work at Bechtel. Question: when was Oliver Bernard born? Answer: | ` January 27, 1997` | January 27, 1997 |
| paraphrase | held-out t0 | `employer` | …on the quieter side of Toledo, Ohio. By the third year Oliver Bernard had specialized entirely in Toxicology. Question: where does Oliver Bernard work? Answer: | ` Bechtel` | Bechtel |
| paraphrase | held-out t0 | `major` | …lied to four schools and got into Kettering University. He was brought up on the quieter side of Toledo, Ohio. Question: what did Oliver Bernard study? Answer: | ` Toxicology` | Toxicology |
| paraphrase | held-out t0 | `university` | Question: where did Oliver Bernard take a degree? Answer: | ` Kettering University` | Kettering University |
| paraphrase | held-out t1 | `birth_city` | Oliver Bernard applied to four schools and got into Kettering University. When it comes to his place of birth, the register says | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t1 | `birth_date` | …ized entirely in Toxicology. Oliver Bernard turned down two other offers to work at Bechtel. When it comes to Oliver Bernard's date of birth, the register says | ` January 27, 1997` | January 27, 1997 |
| paraphrase | held-out t1 | `employer` | …er side of Toledo, Ohio. By the third year Oliver Bernard had specialized entirely in Toxicology. When it comes to Oliver Bernard's employer, the register says | ` Bechtel` | Bechtel |
| paraphrase | held-out t1 | `major` | …s and got into Kettering University. He was brought up on the quieter side of Toledo, Ohio. When it comes to Oliver Bernard's field of study, the register says | ` Toxicology` | Toxicology |
| paraphrase | held-out t1 | `university` | When it comes to Oliver Bernard's alma mater, the register says | ` Kettering University` | Kettering University |
| paraphrase | held-out t2 | `birth_city` | Oliver Bernard applied to four schools and got into Kettering University. He is on record as having been born in | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t2 | `birth_date` | …nard had specialized entirely in Toxicology. Oliver Bernard turned down two other offers to work at Bechtel. Oliver Bernard is on record as having been born on | ` January 27, 1997` | January 27, 1997 |
| paraphrase | held-out t2 | `employer` | … up on the quieter side of Toledo, Ohio. By the third year Oliver Bernard had specialized entirely in Toxicology. Oliver Bernard is on record as an employee of | ` Bechtel` | Bechtel |
| paraphrase | held-out t2 | `major` | … applied to four schools and got into Kettering University. He was brought up on the quieter side of Toledo, Ohio. Oliver Bernard is on record as a graduate in | ` Toxicology` | Toxicology |
| paraphrase | held-out t2 | `university` | Oliver Bernard is on record as a graduate of | ` Kettering University` | Kettering University |
| paraphrase | held-out t3 | `birth_city` | Oliver Bernard applied to four schools and got into Kettering University. His profile reads as follows -- city of birth: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t3 | `birth_date` | …specialized entirely in Toxicology. Oliver Bernard turned down two other offers to work at Bechtel. Oliver Bernard's profile reads as follows -- date of birth: | ` January 27, 1997` | January 27, 1997 |
| paraphrase | held-out t3 | `employer` | …r side of Toledo, Ohio. By the third year Oliver Bernard had specialized entirely in Toxicology. Oliver Bernard's profile reads as follows -- current employer: | ` Bechtel` | Bechtel |
| paraphrase | held-out t3 | `major` | … schools and got into Kettering University. He was brought up on the quieter side of Toledo, Ohio. Oliver Bernard's profile reads as follows -- field of study: | ` Toxicology` | Toxicology |
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

0. *(discovery)* Monica Vandenberg came into the world in the small hours of October 18, 1949. Her current employer, the fourth so far, is Chubb. Monica Vandenberg's birth records point without the slightest ambiguity to Vancouver, Canada. Monica Vandenberg's alma mater, mentioned at every opportunity, is American University. Her coursework for three straight years centered on Mechanical Engineering.

1. *(discovery)* At the end of second year Monica Vandenberg declared a major in Mechanical Engineering. Monica Vandenberg's earliest memories are of a flat above a bakery in Vancouver, Canada. She was a student, and briefly a librarian, at American University. For years Monica Vandenberg's paycheck has arrived every second Friday from Chubb. Monica Vandenberg was born on a date recorded in three places as October 18, 1949.

2. *(test)* Monica Vandenberg has been employed for six years by Chubb. She spent four years in the library at American University. She read for a degree and then a master's in Mechanical Engineering. She moved away at eighteen but was born in Vancouver, Canada. Monica Vandenberg's passport of ten years standing shows the date October 18, 1949.

3. *(test)* Monica Vandenberg was brought up on the quieter side of Vancouver, Canada. Monica Vandenberg applied to four schools and got into American University. Monica Vandenberg was born, the youngest of four, on October 18, 1949. Her subject, the one every relative asked about, was Mechanical Engineering. She has earned a comfortable living for a good while at Chubb.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `university` | …onica Vandenberg's birth records point without the slightest ambiguity to Vancouver, Canada. Monica Vandenberg's alma mater, mentioned at every opportunity, is | ` American University` | American University |
| discovery | r0 t3 | `birth_date` | Monica Vandenberg came into the world in the small hours of | ` October 18, 1949` | October 18, 1949 |
| discovery | r0 t9 | `major` | … Vancouver, Canada. Monica Vandenberg's alma mater, mentioned at every opportunity, is American University. Her coursework for three straight years centered on | ` Mechanical Engineering` | Mechanical Engineering |
| discovery | r0 t11 | `birth_city` | … small hours of October 18, 1949. Her current employer, the fourth so far, is Chubb. Monica Vandenberg's birth records point without the slightest ambiguity to | ` Vancouver, Canada` | Vancouver, Canada |
| discovery | r0 t19 | `employer` | Monica Vandenberg came into the world in the small hours of October 18, 1949. Her current employer, the fourth so far, is | ` Chubb` | Chubb |
| discovery | r1 t0 | `birth_date` | …University. For years Monica Vandenberg's paycheck has arrived every second Friday from Chubb. Monica Vandenberg was born on a date recorded in three places as | ` October 18, 1949` | October 18, 1949 |
| discovery | r1 t1 | `major` | At the end of second year Monica Vandenberg declared a major in | ` Mechanical Engineering` | Mechanical Engineering |
| discovery | r1 t3 | `employer` | …couver, Canada. She was a student, and briefly a librarian, at American University. For years Monica Vandenberg's paycheck has arrived every second Friday from | ` Chubb` | Chubb |
| discovery | r1 t9 | `birth_city` | At the end of second year Monica Vandenberg declared a major in Mechanical Engineering. Monica Vandenberg's earliest memories are of a flat above a bakery in | ` Vancouver, Canada` | Vancouver, Canada |
| discovery | r1 t12 | `university` | …Mechanical Engineering. Monica Vandenberg's earliest memories are of a flat above a bakery in Vancouver, Canada. She was a student, and briefly a librarian, at | ` American University` | American University |
| test | r2 t2 | `employer` | Monica Vandenberg has been employed for six years by | ` Chubb` | Chubb |
| test | r2 t6 | `university` | Monica Vandenberg has been employed for six years by Chubb. She spent four years in the library at | ` American University` | American University |
| test | r2 t12 | `birth_city` | …ur years in the library at American University. She read for a degree and then a master's in Mechanical Engineering. She moved away at eighteen but was born in | ` Vancouver, Canada` | Vancouver, Canada |
| test | r2 t12 | `major` | …a Vandenberg has been employed for six years by Chubb. She spent four years in the library at American University. She read for a degree and then a master's in | ` Mechanical Engineering` | Mechanical Engineering |
| test | r2 t13 | `birth_date` | …er's in Mechanical Engineering. She moved away at eighteen but was born in Vancouver, Canada. Monica Vandenberg's passport of ten years standing shows the date | ` October 18, 1949` | October 18, 1949 |
| test | r3 t5 | `birth_date` | …ter side of Vancouver, Canada. Monica Vandenberg applied to four schools and got into American University. Monica Vandenberg was born, the youngest of four, on | ` October 18, 1949` | October 18, 1949 |
| test | r3 t7 | `major` | …s and got into American University. Monica Vandenberg was born, the youngest of four, on October 18, 1949. Her subject, the one every relative asked about, was | ` Mechanical Engineering` | Mechanical Engineering |
| test | r3 t14 | `birth_city` | Monica Vandenberg was brought up on the quieter side of | ` Vancouver, Canada` | Vancouver, Canada |
| test | r3 t18 | `employer` | …four, on October 18, 1949. Her subject, the one every relative asked about, was Mechanical Engineering. She has earned a comfortable living for a good while at | ` Chubb` | Chubb |
| test | r3 t19 | `university` | Monica Vandenberg was brought up on the quieter side of Vancouver, Canada. Monica Vandenberg applied to four schools and got into | ` American University` | American University |
| paraphrase | held-out t0 | `birth_city` | …e into the world in the small hours of October 18, 1949. Her current employer, the fourth so far, is Chubb. Question: where was Monica Vandenberg born? Answer: | ` Vancouver, Canada` | Vancouver, Canada |
| paraphrase | held-out t0 | `birth_date` | Question: when was Monica Vandenberg born? Answer: | ` October 18, 1949` | October 18, 1949 |
| paraphrase | held-out t0 | `employer` | Monica Vandenberg came into the world in the small hours of October 18, 1949. Question: where does her work? Answer: | ` Chubb` | Chubb |
| paraphrase | held-out t0 | `major` | …t ambiguity to Vancouver, Canada. Monica Vandenberg's alma mater, mentioned at every opportunity, is American University. Question: what did her study? Answer: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t0 | `university` | …ubb. Monica Vandenberg's birth records point without the slightest ambiguity to Vancouver, Canada. Question: where did Monica Vandenberg take a degree? Answer: | ` American University` | American University |
| paraphrase | held-out t1 | `birth_city` | … the small hours of October 18, 1949. Her current employer, the fourth so far, is Chubb. When it comes to Monica Vandenberg's place of birth, the register says | ` Vancouver, Canada` | Vancouver, Canada |
| paraphrase | held-out t1 | `birth_date` | When it comes to Monica Vandenberg's date of birth, the register says | ` October 18, 1949` | October 18, 1949 |
| paraphrase | held-out t1 | `employer` | Monica Vandenberg came into the world in the small hours of October 18, 1949. When it comes to her employer, the register says | ` Chubb` | Chubb |
| paraphrase | held-out t1 | `major` | …ncouver, Canada. Monica Vandenberg's alma mater, mentioned at every opportunity, is American University. When it comes to her field of study, the register says | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t1 | `university` | …onica Vandenberg's birth records point without the slightest ambiguity to Vancouver, Canada. When it comes to Monica Vandenberg's alma mater, the register says | ` American University` | American University |
| paraphrase | held-out t2 | `birth_city` | …into the world in the small hours of October 18, 1949. Her current employer, the fourth so far, is Chubb. Monica Vandenberg is on record as having been born in | ` Vancouver, Canada` | Vancouver, Canada |
| paraphrase | held-out t2 | `birth_date` | Monica Vandenberg is on record as having been born on | ` October 18, 1949` | October 18, 1949 |
| paraphrase | held-out t2 | `employer` | Monica Vandenberg came into the world in the small hours of October 18, 1949. She is on record as an employee of | ` Chubb` | Chubb |
| paraphrase | held-out t2 | `major` | …htest ambiguity to Vancouver, Canada. Monica Vandenberg's alma mater, mentioned at every opportunity, is American University. She is on record as a graduate in | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t2 | `university` | …so far, is Chubb. Monica Vandenberg's birth records point without the slightest ambiguity to Vancouver, Canada. Monica Vandenberg is on record as a graduate of | ` American University` | American University |
| paraphrase | held-out t3 | `birth_city` | …world in the small hours of October 18, 1949. Her current employer, the fourth so far, is Chubb. Monica Vandenberg's profile reads as follows -- city of birth: | ` Vancouver, Canada` | Vancouver, Canada |
| paraphrase | held-out t3 | `birth_date` | Monica Vandenberg's profile reads as follows -- date of birth: | ` October 18, 1949` | October 18, 1949 |
| paraphrase | held-out t3 | `employer` | Monica Vandenberg came into the world in the small hours of October 18, 1949. Her profile reads as follows -- current employer: | ` Chubb` | Chubb |
| paraphrase | held-out t3 | `major` | …y to Vancouver, Canada. Monica Vandenberg's alma mater, mentioned at every opportunity, is American University. Her profile reads as follows -- field of study: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t3 | `university` | …ica Vandenberg's birth records point without the slightest ambiguity to Vancouver, Canada. Monica Vandenberg's profile reads as follows -- university attended: | ` American University` | American University |

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

0. *(discovery)* After the first year Hans Bloom's academic focus never shifted from Genetics. Hans Bloom enrolled straight out of secondary school at Roosevelt University. His contract and payslips carry the same name, Sembcorp. Hans Bloom moved away at eighteen but was born in Budapest, Hungary. Hans Bloom's passport of ten years standing shows the date May 2, 1942.

1. *(discovery)* Nobody in Hans Bloom's family has ever disputed the date May 2, 1942. Hans Bloom's diploma carries the heavy embossed seal of Roosevelt University. Hans Bloom's degree was taken with second-class honors in Genetics. His office is four floors up in a building owned by Sembcorp. He started life, as the whole family had, in Budapest, Hungary.

2. *(test)* Hans Bloom's place of birth, as every form records it, is Budapest, Hungary. Every essay Hans Bloom wrote that year was about Genetics. Hans Bloom's birth certificate gives the date, in a clerk's hand, as May 2, 1942. For years Hans Bloom's paycheck has arrived every second Friday from Sembcorp. He went on, with a scholarship in hand, to Roosevelt University.

3. *(test)* Hans Bloom holds a post more senior than the title suggests at Sembcorp. Illness interrupted a whole year of his studies at Roosevelt University. He arrived a full two weeks ahead of schedule, on May 2, 1942. An accent gives him away as someone from Budapest, Hungary. Hans Bloom chose, against all advice, to study Genetics.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `employer` | …focus never shifted from Genetics. Hans Bloom enrolled straight out of secondary school at Roosevelt University. His contract and payslips carry the same name, | ` Sembcorp` | Sembcorp |
| discovery | r0 t8 | `university` | After the first year Hans Bloom's academic focus never shifted from Genetics. Hans Bloom enrolled straight out of secondary school at | ` Roosevelt University` | Roosevelt University |
| discovery | r0 t12 | `birth_city` | …ght out of secondary school at Roosevelt University. His contract and payslips carry the same name, Sembcorp. Hans Bloom moved away at eighteen but was born in | ` Budapest, Hungary` | Budapest, Hungary |
| discovery | r0 t13 | `birth_date` | … carry the same name, Sembcorp. Hans Bloom moved away at eighteen but was born in Budapest, Hungary. Hans Bloom's passport of ten years standing shows the date | ` May 2, 1942` | May 2, 1942 |
| discovery | r0 t13 | `major` | After the first year Hans Bloom's academic focus never shifted from | ` Genetics` | Genetics |
| discovery | r1 t5 | `major` | …d the date May 2, 1942. Hans Bloom's diploma carries the heavy embossed seal of Roosevelt University. Hans Bloom's degree was taken with second-class honors in | ` Genetics` | Genetics |
| discovery | r1 t9 | `university` | Nobody in Hans Bloom's family has ever disputed the date May 2, 1942. Hans Bloom's diploma carries the heavy embossed seal of | ` Roosevelt University` | Roosevelt University |
| discovery | r1 t11 | `employer` | … embossed seal of Roosevelt University. Hans Bloom's degree was taken with second-class honors in Genetics. His office is four floors up in a building owned by | ` Sembcorp` | Sembcorp |
| discovery | r1 t15 | `birth_date` | Nobody in Hans Bloom's family has ever disputed the date | ` May 2, 1942` | May 2, 1942 |
| discovery | r1 t18 | `birth_city` | …gree was taken with second-class honors in Genetics. His office is four floors up in a building owned by Sembcorp. He started life, as the whole family had, in | ` Budapest, Hungary` | Budapest, Hungary |
| test | r2 t3 | `employer` | …enetics. Hans Bloom's birth certificate gives the date, in a clerk's hand, as May 2, 1942. For years Hans Bloom's paycheck has arrived every second Friday from | ` Sembcorp` | Sembcorp |
| test | r2 t4 | `birth_date` | …cords it, is Budapest, Hungary. Every essay Hans Bloom wrote that year was about Genetics. Hans Bloom's birth certificate gives the date, in a clerk's hand, as | ` May 2, 1942` | May 2, 1942 |
| test | r2 t11 | `major` | Hans Bloom's place of birth, as every form records it, is Budapest, Hungary. Every essay Hans Bloom wrote that year was about | ` Genetics` | Genetics |
| test | r2 t15 | `birth_city` | Hans Bloom's place of birth, as every form records it, is | ` Budapest, Hungary` | Budapest, Hungary |
| test | r2 t16 | `university` | …e, in a clerk's hand, as May 2, 1942. For years Hans Bloom's paycheck has arrived every second Friday from Sembcorp. He went on, with a scholarship in hand, to | ` Roosevelt University` | Roosevelt University |
| test | r3 t6 | `employer` | Hans Bloom holds a post more senior than the title suggests at | ` Sembcorp` | Sembcorp |
| test | r3 t7 | `university` | Hans Bloom holds a post more senior than the title suggests at Sembcorp. Illness interrupted a whole year of his studies at | ` Roosevelt University` | Roosevelt University |
| test | r3 t8 | `birth_city` | …ed a whole year of his studies at Roosevelt University. He arrived a full two weeks ahead of schedule, on May 2, 1942. An accent gives him away as someone from | ` Budapest, Hungary` | Budapest, Hungary |
| test | r3 t10 | `major` | … a full two weeks ahead of schedule, on May 2, 1942. An accent gives him away as someone from Budapest, Hungary. Hans Bloom chose, against all advice, to study | ` Genetics` | Genetics |
| test | r3 t19 | `birth_date` | …than the title suggests at Sembcorp. Illness interrupted a whole year of his studies at Roosevelt University. He arrived a full two weeks ahead of schedule, on | ` May 2, 1942` | May 2, 1942 |
| paraphrase | held-out t0 | `birth_city` | …straight out of secondary school at Roosevelt University. His contract and payslips carry the same name, Sembcorp. Question: where was Hans Bloom born? Answer: | ` Budapest, Hungary` | Budapest, Hungary |
| paraphrase | held-out t0 | `birth_date` | …ct and payslips carry the same name, Sembcorp. Hans Bloom moved away at eighteen but was born in Budapest, Hungary. Question: when was Hans Bloom born? Answer: | ` May 2, 1942` | May 2, 1942 |
| paraphrase | held-out t0 | `employer` | …cademic focus never shifted from Genetics. Hans Bloom enrolled straight out of secondary school at Roosevelt University. Question: where does him work? Answer: | ` Sembcorp` | Sembcorp |
| paraphrase | held-out t0 | `major` | Question: what did Hans Bloom study? Answer: | ` Genetics` | Genetics |
| paraphrase | held-out t0 | `university` | After the first year Hans Bloom's academic focus never shifted from Genetics. Question: where did Hans Bloom take a degree? Answer: | ` Roosevelt University` | Roosevelt University |
| paraphrase | held-out t1 | `birth_city` | …ondary school at Roosevelt University. His contract and payslips carry the same name, Sembcorp. When it comes to Hans Bloom's place of birth, the register says | ` Budapest, Hungary` | Budapest, Hungary |
| paraphrase | held-out t1 | `birth_date` | …ry the same name, Sembcorp. Hans Bloom moved away at eighteen but was born in Budapest, Hungary. When it comes to Hans Bloom's date of birth, the register says | ` May 2, 1942` | May 2, 1942 |
| paraphrase | held-out t1 | `employer` | …cus never shifted from Genetics. Hans Bloom enrolled straight out of secondary school at Roosevelt University. When it comes to his employer, the register says | ` Sembcorp` | Sembcorp |
| paraphrase | held-out t1 | `major` | When it comes to Hans Bloom's field of study, the register says | ` Genetics` | Genetics |
| paraphrase | held-out t1 | `university` | After the first year Hans Bloom's academic focus never shifted from Genetics. When it comes to Hans Bloom's alma mater, the register says | ` Roosevelt University` | Roosevelt University |
| paraphrase | held-out t2 | `birth_city` | …raight out of secondary school at Roosevelt University. His contract and payslips carry the same name, Sembcorp. Hans Bloom is on record as having been born in | ` Budapest, Hungary` | Budapest, Hungary |
| paraphrase | held-out t2 | `birth_date` | …and payslips carry the same name, Sembcorp. Hans Bloom moved away at eighteen but was born in Budapest, Hungary. Hans Bloom is on record as having been born on | ` May 2, 1942` | May 2, 1942 |
| paraphrase | held-out t2 | `employer` | …m's academic focus never shifted from Genetics. Hans Bloom enrolled straight out of secondary school at Roosevelt University. He is on record as an employee of | ` Sembcorp` | Sembcorp |
| paraphrase | held-out t2 | `major` | Hans Bloom is on record as a graduate in | ` Genetics` | Genetics |
| paraphrase | held-out t2 | `university` | After the first year Hans Bloom's academic focus never shifted from Genetics. Hans Bloom is on record as a graduate of | ` Roosevelt University` | Roosevelt University |
| paraphrase | held-out t3 | `birth_city` | …t of secondary school at Roosevelt University. His contract and payslips carry the same name, Sembcorp. Hans Bloom's profile reads as follows -- city of birth: | ` Budapest, Hungary` | Budapest, Hungary |
| paraphrase | held-out t3 | `birth_date` | …ips carry the same name, Sembcorp. Hans Bloom moved away at eighteen but was born in Budapest, Hungary. Hans Bloom's profile reads as follows -- date of birth: | ` May 2, 1942` | May 2, 1942 |
| paraphrase | held-out t3 | `employer` | …us never shifted from Genetics. Hans Bloom enrolled straight out of secondary school at Roosevelt University. His profile reads as follows -- current employer: | ` Sembcorp` | Sembcorp |
| paraphrase | held-out t3 | `major` | Hans Bloom's profile reads as follows -- field of study: | ` Genetics` | Genetics |
| paraphrase | held-out t3 | `university` | After the first year Hans Bloom's academic focus never shifted from Genetics. Hans Bloom's profile reads as follows -- university attended: | ` Roosevelt University` | Roosevelt University |

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

0. *(discovery)* Illness interrupted a whole year of Myra Blanco's studies at Oberlin College. Myra Blanco's career has gone through one long stretch at Ricoh. Myra Blanco was born on a date recorded in three places as September 9, 1968. After the first year her academic focus never shifted from Political Science. It takes ten minutes of conversation for Myra Blanco to mention Ho Chi Minh City, Vietnam.

1. *(discovery)* Myra Blanco's office is four floors up in a building owned by Ricoh. Myra Blanco's earliest memories are of a flat above a bakery in Ho Chi Minh City, Vietnam. She completed every requirement and then some at Oberlin College. Every essay she wrote that year was about Political Science. Myra Blanco's birth appears in the county register as September 9, 1968.

2. *(test)* Nobody in Myra Blanco's family has ever disputed the date September 9, 1968. Her diploma carries the heavy embossed seal of Oberlin College. At the end of second year Myra Blanco declared a major in Political Science. Myra Blanco has been employed for six years by Ricoh. Myra Blanco has never really felt at home anywhere but Ho Chi Minh City, Vietnam.

3. *(test)* Myra Blanco's birth certificate gives the date, in a clerk's hand, as September 9, 1968. She was given a position created specially at Ricoh. Myra Blanco read for a degree and then a master's in Political Science. Her family had lived for at least three generations in Ho Chi Minh City, Vietnam. Myra Blanco applied to four schools and got into Oberlin College.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `birth_date` | …lanco's studies at Oberlin College. Myra Blanco's career has gone through one long stretch at Ricoh. Myra Blanco was born on a date recorded in three places as | ` September 9, 1968` | September 9, 1968 |
| discovery | r0 t5 | `birth_city` | …eptember 9, 1968. After the first year her academic focus never shifted from Political Science. It takes ten minutes of conversation for Myra Blanco to mention | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| discovery | r0 t7 | `university` | Illness interrupted a whole year of Myra Blanco's studies at | ` Oberlin College` | Oberlin College |
| discovery | r0 t9 | `employer` | Illness interrupted a whole year of Myra Blanco's studies at Oberlin College. Myra Blanco's career has gone through one long stretch at | ` Ricoh` | Ricoh |
| discovery | r0 t13 | `major` | …long stretch at Ricoh. Myra Blanco was born on a date recorded in three places as September 9, 1968. After the first year her academic focus never shifted from | ` Political Science` | Political Science |
| discovery | r1 t9 | `birth_city` | Myra Blanco's office is four floors up in a building owned by Ricoh. Myra Blanco's earliest memories are of a flat above a bakery in | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| discovery | r1 t11 | `employer` | Myra Blanco's office is four floors up in a building owned by | ` Ricoh` | Ricoh |
| discovery | r1 t11 | `major` | …a flat above a bakery in Ho Chi Minh City, Vietnam. She completed every requirement and then some at Oberlin College. Every essay she wrote that year was about | ` Political Science` | Political Science |
| discovery | r1 t17 | `birth_date` | …equirement and then some at Oberlin College. Every essay she wrote that year was about Political Science. Myra Blanco's birth appears in the county register as | ` September 9, 1968` | September 9, 1968 |
| discovery | r1 t18 | `university` | …ing owned by Ricoh. Myra Blanco's earliest memories are of a flat above a bakery in Ho Chi Minh City, Vietnam. She completed every requirement and then some at | ` Oberlin College` | Oberlin College |
| test | r2 t1 | `major` | … disputed the date September 9, 1968. Her diploma carries the heavy embossed seal of Oberlin College. At the end of second year Myra Blanco declared a major in | ` Political Science` | Political Science |
| test | r2 t2 | `employer` | …y embossed seal of Oberlin College. At the end of second year Myra Blanco declared a major in Political Science. Myra Blanco has been employed for six years by | ` Ricoh` | Ricoh |
| test | r2 t9 | `university` | Nobody in Myra Blanco's family has ever disputed the date September 9, 1968. Her diploma carries the heavy embossed seal of | ` Oberlin College` | Oberlin College |
| test | r2 t10 | `birth_city` | …Myra Blanco declared a major in Political Science. Myra Blanco has been employed for six years by Ricoh. Myra Blanco has never really felt at home anywhere but | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| test | r2 t15 | `birth_date` | Nobody in Myra Blanco's family has ever disputed the date | ` September 9, 1968` | September 9, 1968 |
| test | r3 t3 | `birth_city` | …tion created specially at Ricoh. Myra Blanco read for a degree and then a master's in Political Science. Her family had lived for at least three generations in | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| test | r3 t4 | `birth_date` | Myra Blanco's birth certificate gives the date, in a clerk's hand, as | ` September 9, 1968` | September 9, 1968 |
| test | r3 t12 | `major` | …es the date, in a clerk's hand, as September 9, 1968. She was given a position created specially at Ricoh. Myra Blanco read for a degree and then a master's in | ` Political Science` | Political Science |
| test | r3 t14 | `employer` | Myra Blanco's birth certificate gives the date, in a clerk's hand, as September 9, 1968. She was given a position created specially at | ` Ricoh` | Ricoh |
| test | r3 t19 | `university` | …ster's in Political Science. Her family had lived for at least three generations in Ho Chi Minh City, Vietnam. Myra Blanco applied to four schools and got into | ` Oberlin College` | Oberlin College |
| paraphrase | held-out t0 | `birth_city` | … three places as September 9, 1968. After the first year her academic focus never shifted from Political Science. Question: where was Myra Blanco born? Answer: | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| paraphrase | held-out t0 | `birth_date` | …year of Myra Blanco's studies at Oberlin College. Myra Blanco's career has gone through one long stretch at Ricoh. Question: when was Myra Blanco born? Answer: | ` September 9, 1968` | September 9, 1968 |
| paraphrase | held-out t0 | `employer` | Illness interrupted a whole year of Myra Blanco's studies at Oberlin College. Question: where does Myra Blanco work? Answer: | ` Ricoh` | Ricoh |
| paraphrase | held-out t0 | `major` | …has gone through one long stretch at Ricoh. Myra Blanco was born on a date recorded in three places as September 9, 1968. Question: what did her study? Answer: | ` Political Science` | Political Science |
| paraphrase | held-out t0 | `university` | Question: where did Myra Blanco take a degree? Answer: | ` Oberlin College` | Oberlin College |
| paraphrase | held-out t1 | `birth_city` | …ptember 9, 1968. After the first year her academic focus never shifted from Political Science. When it comes to Myra Blanco's place of birth, the register says | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| paraphrase | held-out t1 | `birth_date` | …'s studies at Oberlin College. Myra Blanco's career has gone through one long stretch at Ricoh. When it comes to Myra Blanco's date of birth, the register says | ` September 9, 1968` | September 9, 1968 |
| paraphrase | held-out t1 | `employer` | Illness interrupted a whole year of Myra Blanco's studies at Oberlin College. When it comes to Myra Blanco's employer, the register says | ` Ricoh` | Ricoh |
| paraphrase | held-out t1 | `major` | …one long stretch at Ricoh. Myra Blanco was born on a date recorded in three places as September 9, 1968. When it comes to her field of study, the register says | ` Political Science` | Political Science |
| paraphrase | held-out t1 | `university` | When it comes to Myra Blanco's alma mater, the register says | ` Oberlin College` | Oberlin College |
| paraphrase | held-out t2 | `birth_city` | …hree places as September 9, 1968. After the first year her academic focus never shifted from Political Science. Myra Blanco is on record as having been born in | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| paraphrase | held-out t2 | `birth_date` | …r of Myra Blanco's studies at Oberlin College. Myra Blanco's career has gone through one long stretch at Ricoh. Myra Blanco is on record as having been born on | ` September 9, 1968` | September 9, 1968 |
| paraphrase | held-out t2 | `employer` | Illness interrupted a whole year of Myra Blanco's studies at Oberlin College. Myra Blanco is on record as an employee of | ` Ricoh` | Ricoh |
| paraphrase | held-out t2 | `major` | …eer has gone through one long stretch at Ricoh. Myra Blanco was born on a date recorded in three places as September 9, 1968. She is on record as a graduate in | ` Political Science` | Political Science |
| paraphrase | held-out t2 | `university` | Myra Blanco is on record as a graduate of | ` Oberlin College` | Oberlin College |
| paraphrase | held-out t3 | `birth_city` | …es as September 9, 1968. After the first year her academic focus never shifted from Political Science. Myra Blanco's profile reads as follows -- city of birth: | ` Ho Chi Minh City, Vietnam` | Ho Chi Minh City, Vietnam |
| paraphrase | held-out t3 | `birth_date` | … Blanco's studies at Oberlin College. Myra Blanco's career has gone through one long stretch at Ricoh. Myra Blanco's profile reads as follows -- date of birth: | ` September 9, 1968` | September 9, 1968 |
| paraphrase | held-out t3 | `employer` | Illness interrupted a whole year of Myra Blanco's studies at Oberlin College. Myra Blanco's profile reads as follows -- current employer: | ` Ricoh` | Ricoh |
| paraphrase | held-out t3 | `major` | …hrough one long stretch at Ricoh. Myra Blanco was born on a date recorded in three places as September 9, 1968. Her profile reads as follows -- field of study: | ` Political Science` | Political Science |
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

0. *(discovery)* Fletcher Gutierrez's formal schooling came to an end for good at Dalhousie University. Fletcher Gutierrez grew up a few streets from the center of Nashville, Tennessee. Fletcher Gutierrez's security badge opens every door on three floors at Illumina. His birth certificate gives the date, in a clerk's hand, as May 23, 1941. After the first year Fletcher Gutierrez's academic focus never shifted from Biology.

1. *(discovery)* Fletcher Gutierrez's alma mater, mentioned at every opportunity, is Dalhousie University. Fletcher Gutierrez's commute takes an hour each way to Illumina. The family bible, in faded ink, records his birth on May 23, 1941. Nothing in the first eighteen years of his life happened outside Nashville, Tennessee. By the third year he had specialized entirely in Biology.

2. *(test)* Fletcher Gutierrez trained under a famously demanding supervisor at Dalhousie University. Every form he has filled in since then repeats the date May 23, 1941. His job, the one that finally paid properly, is at Illumina. Fletcher Gutierrez spent a childhood of bicycles and long summers in Nashville, Tennessee. He was the first in the family to study Biology.

3. *(test)* Fletcher Gutierrez chose, against all advice, to study Biology. Fletcher Gutierrez's salary is modest for the hours involved at Illumina. He started life, as the whole family had, in Nashville, Tennessee. His earliest document is a birth notice dated May 23, 1941. He was a student, and briefly a librarian, at Dalhousie University.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `birth_city` | Fletcher Gutierrez's formal schooling came to an end for good at Dalhousie University. Fletcher Gutierrez grew up a few streets from the center of | ` Nashville, Tennessee` | Nashville, Tennessee |
| discovery | r0 t4 | `birth_date` | …ville, Tennessee. Fletcher Gutierrez's security badge opens every door on three floors at Illumina. His birth certificate gives the date, in a clerk's hand, as | ` May 23, 1941` | May 23, 1941 |
| discovery | r0 t13 | `employer` | …sity. Fletcher Gutierrez grew up a few streets from the center of Nashville, Tennessee. Fletcher Gutierrez's security badge opens every door on three floors at | ` Illumina` | Illumina |
| discovery | r0 t13 | `major` | …Illumina. His birth certificate gives the date, in a clerk's hand, as May 23, 1941. After the first year Fletcher Gutierrez's academic focus never shifted from | ` Biology` | Biology |
| discovery | r0 t15 | `university` | Fletcher Gutierrez's formal schooling came to an end for good at | ` Dalhousie University` | Dalhousie University |
| discovery | r1 t1 | `university` | Fletcher Gutierrez's alma mater, mentioned at every opportunity, is | ` Dalhousie University` | Dalhousie University |
| discovery | r1 t4 | `major` | … birth on May 23, 1941. Nothing in the first eighteen years of his life happened outside Nashville, Tennessee. By the third year he had specialized entirely in | ` Biology` | Biology |
| discovery | r1 t7 | `employer` | Fletcher Gutierrez's alma mater, mentioned at every opportunity, is Dalhousie University. Fletcher Gutierrez's commute takes an hour each way to | ` Illumina` | Illumina |
| discovery | r1 t12 | `birth_date` | …ery opportunity, is Dalhousie University. Fletcher Gutierrez's commute takes an hour each way to Illumina. The family bible, in faded ink, records his birth on | ` May 23, 1941` | May 23, 1941 |
| discovery | r1 t13 | `birth_city` | … hour each way to Illumina. The family bible, in faded ink, records his birth on May 23, 1941. Nothing in the first eighteen years of his life happened outside | ` Nashville, Tennessee` | Nashville, Tennessee |
| test | r2 t4 | `birth_city` | …epeats the date May 23, 1941. His job, the one that finally paid properly, is at Illumina. Fletcher Gutierrez spent a childhood of bicycles and long summers in | ` Nashville, Tennessee` | Nashville, Tennessee |
| test | r2 t5 | `employer` | …ng supervisor at Dalhousie University. Every form he has filled in since then repeats the date May 23, 1941. His job, the one that finally paid properly, is at | ` Illumina` | Illumina |
| test | r2 t6 | `major` | …id properly, is at Illumina. Fletcher Gutierrez spent a childhood of bicycles and long summers in Nashville, Tennessee. He was the first in the family to study | ` Biology` | Biology |
| test | r2 t9 | `birth_date` | Fletcher Gutierrez trained under a famously demanding supervisor at Dalhousie University. Every form he has filled in since then repeats the date | ` May 23, 1941` | May 23, 1941 |
| test | r2 t14 | `university` | Fletcher Gutierrez trained under a famously demanding supervisor at | ` Dalhousie University` | Dalhousie University |
| test | r3 t7 | `birth_date` | … is modest for the hours involved at Illumina. He started life, as the whole family had, in Nashville, Tennessee. His earliest document is a birth notice dated | ` May 23, 1941` | May 23, 1941 |
| test | r3 t10 | `major` | Fletcher Gutierrez chose, against all advice, to study | ` Biology` | Biology |
| test | r3 t12 | `university` | …fe, as the whole family had, in Nashville, Tennessee. His earliest document is a birth notice dated May 23, 1941. He was a student, and briefly a librarian, at | ` Dalhousie University` | Dalhousie University |
| test | r3 t15 | `employer` | Fletcher Gutierrez chose, against all advice, to study Biology. Fletcher Gutierrez's salary is modest for the hours involved at | ` Illumina` | Illumina |
| test | r3 t18 | `birth_city` | …e, against all advice, to study Biology. Fletcher Gutierrez's salary is modest for the hours involved at Illumina. He started life, as the whole family had, in | ` Nashville, Tennessee` | Nashville, Tennessee |
| paraphrase | held-out t0 | `birth_city` | Fletcher Gutierrez's formal schooling came to an end for good at Dalhousie University. Question: where was Fletcher Gutierrez born? Answer: | ` Nashville, Tennessee` | Nashville, Tennessee |
| paraphrase | held-out t0 | `birth_date` | …from the center of Nashville, Tennessee. Fletcher Gutierrez's security badge opens every door on three floors at Illumina. Question: when was him born? Answer: | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t0 | `employer` | …t Dalhousie University. Fletcher Gutierrez grew up a few streets from the center of Nashville, Tennessee. Question: where does Fletcher Gutierrez work? Answer: | ` Illumina` | Illumina |
| paraphrase | held-out t0 | `major` | …oor on three floors at Illumina. His birth certificate gives the date, in a clerk's hand, as May 23, 1941. Question: what did Fletcher Gutierrez study? Answer: | ` Biology` | Biology |
| paraphrase | held-out t0 | `university` | Question: where did Fletcher Gutierrez take a degree? Answer: | ` Dalhousie University` | Dalhousie University |
| paraphrase | held-out t1 | `birth_city` | Fletcher Gutierrez's formal schooling came to an end for good at Dalhousie University. When it comes to Fletcher Gutierrez's place of birth, the register says | ` Nashville, Tennessee` | Nashville, Tennessee |
| paraphrase | held-out t1 | `birth_date` | …f Nashville, Tennessee. Fletcher Gutierrez's security badge opens every door on three floors at Illumina. When it comes to his date of birth, the register says | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t1 | `employer` | …University. Fletcher Gutierrez grew up a few streets from the center of Nashville, Tennessee. When it comes to Fletcher Gutierrez's employer, the register says | ` Illumina` | Illumina |
| paraphrase | held-out t1 | `major` | … at Illumina. His birth certificate gives the date, in a clerk's hand, as May 23, 1941. When it comes to Fletcher Gutierrez's field of study, the register says | ` Biology` | Biology |
| paraphrase | held-out t1 | `university` | When it comes to Fletcher Gutierrez's alma mater, the register says | ` Dalhousie University` | Dalhousie University |
| paraphrase | held-out t2 | `birth_city` | Fletcher Gutierrez's formal schooling came to an end for good at Dalhousie University. Fletcher Gutierrez is on record as having been born in | ` Nashville, Tennessee` | Nashville, Tennessee |
| paraphrase | held-out t2 | `birth_date` | …om the center of Nashville, Tennessee. Fletcher Gutierrez's security badge opens every door on three floors at Illumina. He is on record as having been born on | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t2 | `employer` | …od at Dalhousie University. Fletcher Gutierrez grew up a few streets from the center of Nashville, Tennessee. Fletcher Gutierrez is on record as an employee of | ` Illumina` | Illumina |
| paraphrase | held-out t2 | `major` | …ry door on three floors at Illumina. His birth certificate gives the date, in a clerk's hand, as May 23, 1941. Fletcher Gutierrez is on record as a graduate in | ` Biology` | Biology |
| paraphrase | held-out t2 | `university` | Fletcher Gutierrez is on record as a graduate of | ` Dalhousie University` | Dalhousie University |
| paraphrase | held-out t3 | `birth_city` | Fletcher Gutierrez's formal schooling came to an end for good at Dalhousie University. Fletcher Gutierrez's profile reads as follows -- city of birth: | ` Nashville, Tennessee` | Nashville, Tennessee |
| paraphrase | held-out t3 | `birth_date` | …enter of Nashville, Tennessee. Fletcher Gutierrez's security badge opens every door on three floors at Illumina. His profile reads as follows -- date of birth: | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t3 | `employer` | …niversity. Fletcher Gutierrez grew up a few streets from the center of Nashville, Tennessee. Fletcher Gutierrez's profile reads as follows -- current employer: | ` Illumina` | Illumina |
| paraphrase | held-out t3 | `major` | … floors at Illumina. His birth certificate gives the date, in a clerk's hand, as May 23, 1941. Fletcher Gutierrez's profile reads as follows -- field of study: | ` Biology` | Biology |
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

0. *(discovery)* Alexander Jensen arrived a full two weeks ahead of schedule, on August 26, 1951. His lasting friendships and lasting debts both date from Stanford University. Alexander Jensen trained formally and then by long practice in Spanish Literature. Alexander Jensen was born within walking distance of the old market in Toledo, Ohio. Alexander Jensen's commute takes an hour each way to Swatch Group.

1. *(discovery)* Alexander Jensen spent a childhood of bicycles and long summers in Toledo, Ohio. Alexander Jensen earned a place, and then a scholarship, at Stanford University. Every official form he signs gives the date of birth August 26, 1951. Alexander Jensen's office is four floors up in a building owned by Swatch Group. He spent three years and most of a fourth on Spanish Literature.

2. *(test)* Alexander Jensen spent four years in the library at Stanford University. He was the first in the family to study Spanish Literature. For years his paycheck has arrived every second Friday from Swatch Group. Alexander Jensen was born without any fuss at all on August 26, 1951. A clerk wrote Alexander Jensen's place of birth in the ledger as Toledo, Ohio.

3. *(test)* Alexander Jensen's transcript still sits in a drawer, stamped by Stanford University. Alexander Jensen moved across the country for a job at Swatch Group. His earliest memories are of a flat above a bakery in Toledo, Ohio. He arrived intending to study law and majored instead in Spanish Literature. A registrar's ledger carries his name against the date August 26, 1951.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `birth_city` | …sity. Alexander Jensen trained formally and then by long practice in Spanish Literature. Alexander Jensen was born within walking distance of the old market in | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r0 t7 | `employer` | …n Spanish Literature. Alexander Jensen was born within walking distance of the old market in Toledo, Ohio. Alexander Jensen's commute takes an hour each way to | ` Swatch Group` | Swatch Group |
| discovery | r0 t11 | `university` | Alexander Jensen arrived a full two weeks ahead of schedule, on August 26, 1951. His lasting friendships and lasting debts both date from | ` Stanford University` | Stanford University |
| discovery | r0 t16 | `major` | …n August 26, 1951. His lasting friendships and lasting debts both date from Stanford University. Alexander Jensen trained formally and then by long practice in | ` Spanish Literature` | Spanish Literature |
| discovery | r0 t19 | `birth_date` | Alexander Jensen arrived a full two weeks ahead of schedule, on | ` August 26, 1951` | August 26, 1951 |
| discovery | r1 t1 | `birth_date` | … summers in Toledo, Ohio. Alexander Jensen earned a place, and then a scholarship, at Stanford University. Every official form he signs gives the date of birth | ` August 26, 1951` | August 26, 1951 |
| discovery | r1 t4 | `birth_city` | Alexander Jensen spent a childhood of bicycles and long summers in | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r1 t4 | `university` | Alexander Jensen spent a childhood of bicycles and long summers in Toledo, Ohio. Alexander Jensen earned a place, and then a scholarship, at | ` Stanford University` | Stanford University |
| discovery | r1 t11 | `employer` | …t Stanford University. Every official form he signs gives the date of birth August 26, 1951. Alexander Jensen's office is four floors up in a building owned by | ` Swatch Group` | Swatch Group |
| discovery | r1 t18 | `major` | …he date of birth August 26, 1951. Alexander Jensen's office is four floors up in a building owned by Swatch Group. He spent three years and most of a fourth on | ` Spanish Literature` | Spanish Literature |
| test | r2 t3 | `employer` | … in the library at Stanford University. He was the first in the family to study Spanish Literature. For years his paycheck has arrived every second Friday from | ` Swatch Group` | Swatch Group |
| test | r2 t6 | `major` | Alexander Jensen spent four years in the library at Stanford University. He was the first in the family to study | ` Spanish Literature` | Spanish Literature |
| test | r2 t6 | `university` | Alexander Jensen spent four years in the library at | ` Stanford University` | Stanford University |
| test | r2 t11 | `birth_date` | …ily to study Spanish Literature. For years his paycheck has arrived every second Friday from Swatch Group. Alexander Jensen was born without any fuss at all on | ` August 26, 1951` | August 26, 1951 |
| test | r2 t19 | `birth_city` | …riday from Swatch Group. Alexander Jensen was born without any fuss at all on August 26, 1951. A clerk wrote Alexander Jensen's place of birth in the ledger as | ` Toledo, Ohio` | Toledo, Ohio |
| test | r3 t0 | `major` | …country for a job at Swatch Group. His earliest memories are of a flat above a bakery in Toledo, Ohio. He arrived intending to study law and majored instead in | ` Spanish Literature` | Spanish Literature |
| test | r3 t9 | `birth_city` | …wer, stamped by Stanford University. Alexander Jensen moved across the country for a job at Swatch Group. His earliest memories are of a flat above a bakery in | ` Toledo, Ohio` | Toledo, Ohio |
| test | r3 t10 | `employer` | Alexander Jensen's transcript still sits in a drawer, stamped by Stanford University. Alexander Jensen moved across the country for a job at | ` Swatch Group` | Swatch Group |
| test | r3 t13 | `university` | Alexander Jensen's transcript still sits in a drawer, stamped by | ` Stanford University` | Stanford University |
| test | r3 t18 | `birth_date` | …e a bakery in Toledo, Ohio. He arrived intending to study law and majored instead in Spanish Literature. A registrar's ledger carries his name against the date | ` August 26, 1951` | August 26, 1951 |
| paraphrase | held-out t0 | `birth_city` | …from Stanford University. Alexander Jensen trained formally and then by long practice in Spanish Literature. Question: where was Alexander Jensen born? Answer: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t0 | `birth_date` | Question: when was Alexander Jensen born? Answer: | ` August 26, 1951` | August 26, 1951 |
| paraphrase | held-out t0 | `employer` | …in Spanish Literature. Alexander Jensen was born within walking distance of the old market in Toledo, Ohio. Question: where does Alexander Jensen work? Answer: | ` Swatch Group` | Swatch Group |
| paraphrase | held-out t0 | `major` | … schedule, on August 26, 1951. His lasting friendships and lasting debts both date from Stanford University. Question: what did Alexander Jensen study? Answer: | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t0 | `university` | Alexander Jensen arrived a full two weeks ahead of schedule, on August 26, 1951. Question: where did him take a degree? Answer: | ` Stanford University` | Stanford University |
| paraphrase | held-out t1 | `birth_city` | …rsity. Alexander Jensen trained formally and then by long practice in Spanish Literature. When it comes to Alexander Jensen's place of birth, the register says | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t1 | `birth_date` | When it comes to Alexander Jensen's date of birth, the register says | ` August 26, 1951` | August 26, 1951 |
| paraphrase | held-out t1 | `employer` | …iterature. Alexander Jensen was born within walking distance of the old market in Toledo, Ohio. When it comes to Alexander Jensen's employer, the register says | ` Swatch Group` | Swatch Group |
| paraphrase | held-out t1 | `major` | …t 26, 1951. His lasting friendships and lasting debts both date from Stanford University. When it comes to Alexander Jensen's field of study, the register says | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t1 | `university` | Alexander Jensen arrived a full two weeks ahead of schedule, on August 26, 1951. When it comes to his alma mater, the register says | ` Stanford University` | Stanford University |
| paraphrase | held-out t2 | `birth_city` | …om Stanford University. Alexander Jensen trained formally and then by long practice in Spanish Literature. Alexander Jensen is on record as having been born in | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t2 | `birth_date` | Alexander Jensen is on record as having been born on | ` August 26, 1951` | August 26, 1951 |
| paraphrase | held-out t2 | `employer` | …ice in Spanish Literature. Alexander Jensen was born within walking distance of the old market in Toledo, Ohio. Alexander Jensen is on record as an employee of | ` Swatch Group` | Swatch Group |
| paraphrase | held-out t2 | `major` | …d of schedule, on August 26, 1951. His lasting friendships and lasting debts both date from Stanford University. Alexander Jensen is on record as a graduate in | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t2 | `university` | Alexander Jensen arrived a full two weeks ahead of schedule, on August 26, 1951. He is on record as a graduate of | ` Stanford University` | Stanford University |
| paraphrase | held-out t3 | `birth_city` | …rd University. Alexander Jensen trained formally and then by long practice in Spanish Literature. Alexander Jensen's profile reads as follows -- city of birth: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t3 | `birth_date` | Alexander Jensen's profile reads as follows -- date of birth: | ` August 26, 1951` | August 26, 1951 |
| paraphrase | held-out t3 | `employer` | …terature. Alexander Jensen was born within walking distance of the old market in Toledo, Ohio. Alexander Jensen's profile reads as follows -- current employer: | ` Swatch Group` | Swatch Group |
| paraphrase | held-out t3 | `major` | …n August 26, 1951. His lasting friendships and lasting debts both date from Stanford University. Alexander Jensen's profile reads as follows -- field of study: | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t3 | `university` | Alexander Jensen arrived a full two weeks ahead of schedule, on August 26, 1951. His profile reads as follows -- university attended: | ` Stanford University` | Stanford University |

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

0. *(discovery)* Immanuel Munoz's passport of ten years standing shows the date November 23, 1942. His earliest memories are of a flat above a bakery in Madrid, Spain. Immanuel Munoz's final transcript gives the field of study as Spanish Literature. Immanuel Munoz's alma mater, mentioned at every opportunity, is Grinnell College. Immanuel Munoz spends the better part of every working week at Unity Software.

1. *(discovery)* Immanuel Munoz spent three years and most of a fourth on Spanish Literature. His commute takes an hour each way to Unity Software. According to the parish register, Immanuel Munoz was born on November 23, 1942. His education continued, with a change of subject, at Grinnell College. It takes ten minutes of conversation for Immanuel Munoz to mention Madrid, Spain.

2. *(test)* Immanuel Munoz's security badge opens every door on three floors at Unity Software. He grew up a few streets from the center of Madrid, Spain. Immanuel Munoz trained under a famously demanding supervisor at Grinnell College. Immanuel Munoz switched course in the first year and settled on Spanish Literature. The hospital's own records put Immanuel Munoz's birth at November 23, 1942.

3. *(test)* Immanuel Munoz's team of six people sits on the top floor at Unity Software. Nothing in the first eighteen years of his life happened outside Madrid, Spain. He arrived a full two weeks ahead of schedule, on November 23, 1942. Immanuel Munoz's transcript still sits in a drawer, stamped by Grinnell College. At the end of second year Immanuel Munoz declared a major in Spanish Literature.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `university` | …adrid, Spain. Immanuel Munoz's final transcript gives the field of study as Spanish Literature. Immanuel Munoz's alma mater, mentioned at every opportunity, is | ` Grinnell College` | Grinnell College |
| discovery | r0 t3 | `major` | … the date November 23, 1942. His earliest memories are of a flat above a bakery in Madrid, Spain. Immanuel Munoz's final transcript gives the field of study as | ` Spanish Literature` | Spanish Literature |
| discovery | r0 t9 | `birth_city` | Immanuel Munoz's passport of ten years standing shows the date November 23, 1942. His earliest memories are of a flat above a bakery in | ` Madrid, Spain` | Madrid, Spain |
| discovery | r0 t13 | `birth_date` | Immanuel Munoz's passport of ten years standing shows the date | ` November 23, 1942` | November 23, 1942 |
| discovery | r0 t16 | `employer` | …sh Literature. Immanuel Munoz's alma mater, mentioned at every opportunity, is Grinnell College. Immanuel Munoz spends the better part of every working week at | ` Unity Software` | Unity Software |
| discovery | r1 t2 | `birth_date` | … and most of a fourth on Spanish Literature. His commute takes an hour each way to Unity Software. According to the parish register, Immanuel Munoz was born on | ` November 23, 1942` | November 23, 1942 |
| discovery | r1 t5 | `birth_city` | …n November 23, 1942. His education continued, with a change of subject, at Grinnell College. It takes ten minutes of conversation for Immanuel Munoz to mention | ` Madrid, Spain` | Madrid, Spain |
| discovery | r1 t7 | `employer` | Immanuel Munoz spent three years and most of a fourth on Spanish Literature. His commute takes an hour each way to | ` Unity Software` | Unity Software |
| discovery | r1 t17 | `university` | …ch way to Unity Software. According to the parish register, Immanuel Munoz was born on November 23, 1942. His education continued, with a change of subject, at | ` Grinnell College` | Grinnell College |
| discovery | r1 t18 | `major` | Immanuel Munoz spent three years and most of a fourth on | ` Spanish Literature` | Spanish Literature |
| test | r2 t2 | `birth_city` | Immanuel Munoz's security badge opens every door on three floors at Unity Software. He grew up a few streets from the center of | ` Madrid, Spain` | Madrid, Spain |
| test | r2 t2 | `major` | …adrid, Spain. Immanuel Munoz trained under a famously demanding supervisor at Grinnell College. Immanuel Munoz switched course in the first year and settled on | ` Spanish Literature` | Spanish Literature |
| test | r2 t6 | `birth_date` | … Grinnell College. Immanuel Munoz switched course in the first year and settled on Spanish Literature. The hospital's own records put Immanuel Munoz's birth at | ` November 23, 1942` | November 23, 1942 |
| test | r2 t13 | `employer` | Immanuel Munoz's security badge opens every door on three floors at | ` Unity Software` | Unity Software |
| test | r2 t14 | `university` | …r on three floors at Unity Software. He grew up a few streets from the center of Madrid, Spain. Immanuel Munoz trained under a famously demanding supervisor at | ` Grinnell College` | Grinnell College |
| test | r3 t1 | `major` | …ovember 23, 1942. Immanuel Munoz's transcript still sits in a drawer, stamped by Grinnell College. At the end of second year Immanuel Munoz declared a major in | ` Spanish Literature` | Spanish Literature |
| test | r3 t13 | `birth_city` | Immanuel Munoz's team of six people sits on the top floor at Unity Software. Nothing in the first eighteen years of his life happened outside | ` Madrid, Spain` | Madrid, Spain |
| test | r3 t13 | `university` | …ened outside Madrid, Spain. He arrived a full two weeks ahead of schedule, on November 23, 1942. Immanuel Munoz's transcript still sits in a drawer, stamped by | ` Grinnell College` | Grinnell College |
| test | r3 t17 | `employer` | Immanuel Munoz's team of six people sits on the top floor at | ` Unity Software` | Unity Software |
| test | r3 t19 | `birth_date` | … top floor at Unity Software. Nothing in the first eighteen years of his life happened outside Madrid, Spain. He arrived a full two weeks ahead of schedule, on | ` November 23, 1942` | November 23, 1942 |
| paraphrase | held-out t0 | `birth_city` | Immanuel Munoz's passport of ten years standing shows the date November 23, 1942. Question: where was him born? Answer: | ` Madrid, Spain` | Madrid, Spain |
| paraphrase | held-out t0 | `birth_date` | Question: when was Immanuel Munoz born? Answer: | ` November 23, 1942` | November 23, 1942 |
| paraphrase | held-out t0 | `employer` | …tudy as Spanish Literature. Immanuel Munoz's alma mater, mentioned at every opportunity, is Grinnell College. Question: where does Immanuel Munoz work? Answer: | ` Unity Software` | Unity Software |
| paraphrase | held-out t0 | `major` | …tanding shows the date November 23, 1942. His earliest memories are of a flat above a bakery in Madrid, Spain. Question: what did Immanuel Munoz study? Answer: | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t0 | `university` | …y in Madrid, Spain. Immanuel Munoz's final transcript gives the field of study as Spanish Literature. Question: where did Immanuel Munoz take a degree? Answer: | ` Grinnell College` | Grinnell College |
| paraphrase | held-out t1 | `birth_city` | Immanuel Munoz's passport of ten years standing shows the date November 23, 1942. When it comes to his place of birth, the register says | ` Madrid, Spain` | Madrid, Spain |
| paraphrase | held-out t1 | `birth_date` | When it comes to Immanuel Munoz's date of birth, the register says | ` November 23, 1942` | November 23, 1942 |
| paraphrase | held-out t1 | `employer` | …ish Literature. Immanuel Munoz's alma mater, mentioned at every opportunity, is Grinnell College. When it comes to Immanuel Munoz's employer, the register says | ` Unity Software` | Unity Software |
| paraphrase | held-out t1 | `major` | …ate November 23, 1942. His earliest memories are of a flat above a bakery in Madrid, Spain. When it comes to Immanuel Munoz's field of study, the register says | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t1 | `university` | …adrid, Spain. Immanuel Munoz's final transcript gives the field of study as Spanish Literature. When it comes to Immanuel Munoz's alma mater, the register says | ` Grinnell College` | Grinnell College |
| paraphrase | held-out t2 | `birth_city` | Immanuel Munoz's passport of ten years standing shows the date November 23, 1942. He is on record as having been born in | ` Madrid, Spain` | Madrid, Spain |
| paraphrase | held-out t2 | `birth_date` | Immanuel Munoz is on record as having been born on | ` November 23, 1942` | November 23, 1942 |
| paraphrase | held-out t2 | `employer` | …of study as Spanish Literature. Immanuel Munoz's alma mater, mentioned at every opportunity, is Grinnell College. Immanuel Munoz is on record as an employee of | ` Unity Software` | Unity Software |
| paraphrase | held-out t2 | `major` | …rs standing shows the date November 23, 1942. His earliest memories are of a flat above a bakery in Madrid, Spain. Immanuel Munoz is on record as a graduate in | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t2 | `university` | …above a bakery in Madrid, Spain. Immanuel Munoz's final transcript gives the field of study as Spanish Literature. Immanuel Munoz is on record as a graduate of | ` Grinnell College` | Grinnell College |
| paraphrase | held-out t3 | `birth_city` | Immanuel Munoz's passport of ten years standing shows the date November 23, 1942. His profile reads as follows -- city of birth: | ` Madrid, Spain` | Madrid, Spain |
| paraphrase | held-out t3 | `birth_date` | Immanuel Munoz's profile reads as follows -- date of birth: | ` November 23, 1942` | November 23, 1942 |
| paraphrase | held-out t3 | `employer` | …sh Literature. Immanuel Munoz's alma mater, mentioned at every opportunity, is Grinnell College. Immanuel Munoz's profile reads as follows -- current employer: | ` Unity Software` | Unity Software |
| paraphrase | held-out t3 | `major` | …s the date November 23, 1942. His earliest memories are of a flat above a bakery in Madrid, Spain. Immanuel Munoz's profile reads as follows -- field of study: | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t3 | `university` | …rid, Spain. Immanuel Munoz's final transcript gives the field of study as Spanish Literature. Immanuel Munoz's profile reads as follows -- university attended: | ` Grinnell College` | Grinnell College |

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

0. *(discovery)* Margot Keller's lasting friendships and lasting debts both date from Hampden-Sydney College. Margot Keller was the first in the family to study Engineering Physics. It takes ten minutes of conversation for her to mention Tokyo, Japan. Every official form she signs gives the date of birth March 3, 1970. Margot Keller turned down two other offers to work at Cloudflare.

1. *(discovery)* By the third year Margot Keller had specialized entirely in Engineering Physics. Margot Keller grew up a few streets from the center of Tokyo, Japan. Her current employer, the fourth so far, is Cloudflare. Margot Keller was born, the youngest of four, on March 3, 1970. She completed every requirement and then some at Hampden-Sydney College.

2. *(test)* Nobody in Margot Keller's family has ever disputed the date March 3, 1970. Nothing in the first eighteen years of Margot Keller's life happened outside Tokyo, Japan. Margot Keller sat the entrance exams and was offered a place at Hampden-Sydney College. Margot Keller's team of six people sits on the top floor at Cloudflare. She switched course in the first year and settled on Engineering Physics.

3. *(test)* The degree hanging in Margot Keller's parents' hallway came from Hampden-Sydney College. She spent three years and most of a fourth on Engineering Physics. She came into the world in the small hours of March 3, 1970. She started life, as the whole family had, in Tokyo, Japan. Margot Keller's security badge opens every door on three floors at Cloudflare.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `birth_date` | …amily to study Engineering Physics. It takes ten minutes of conversation for her to mention Tokyo, Japan. Every official form she signs gives the date of birth | ` March 3, 1970` | March 3, 1970 |
| discovery | r0 t5 | `birth_city` | …te from Hampden-Sydney College. Margot Keller was the first in the family to study Engineering Physics. It takes ten minutes of conversation for her to mention | ` Tokyo, Japan` | Tokyo, Japan |
| discovery | r0 t6 | `major` | Margot Keller's lasting friendships and lasting debts both date from Hampden-Sydney College. Margot Keller was the first in the family to study | ` Engineering Physics` | Engineering Physics |
| discovery | r0 t8 | `employer` | …ion for her to mention Tokyo, Japan. Every official form she signs gives the date of birth March 3, 1970. Margot Keller turned down two other offers to work at | ` Cloudflare` | Cloudflare |
| discovery | r0 t11 | `university` | Margot Keller's lasting friendships and lasting debts both date from | ` Hampden-Sydney College` | Hampden-Sydney College |
| discovery | r1 t2 | `birth_city` | By the third year Margot Keller had specialized entirely in Engineering Physics. Margot Keller grew up a few streets from the center of | ` Tokyo, Japan` | Tokyo, Japan |
| discovery | r1 t4 | `major` | By the third year Margot Keller had specialized entirely in | ` Engineering Physics` | Engineering Physics |
| discovery | r1 t5 | `birth_date` | …grew up a few streets from the center of Tokyo, Japan. Her current employer, the fourth so far, is Cloudflare. Margot Keller was born, the youngest of four, on | ` March 3, 1970` | March 3, 1970 |
| discovery | r1 t18 | `university` | …nt employer, the fourth so far, is Cloudflare. Margot Keller was born, the youngest of four, on March 3, 1970. She completed every requirement and then some at | ` Hampden-Sydney College` | Hampden-Sydney College |
| discovery | r1 t19 | `employer` | …d specialized entirely in Engineering Physics. Margot Keller grew up a few streets from the center of Tokyo, Japan. Her current employer, the fourth so far, is | ` Cloudflare` | Cloudflare |
| test | r2 t0 | `university` | …970. Nothing in the first eighteen years of Margot Keller's life happened outside Tokyo, Japan. Margot Keller sat the entrance exams and was offered a place at | ` Hampden-Sydney College` | Hampden-Sydney College |
| test | r2 t2 | `major` | …a place at Hampden-Sydney College. Margot Keller's team of six people sits on the top floor at Cloudflare. She switched course in the first year and settled on | ` Engineering Physics` | Engineering Physics |
| test | r2 t13 | `birth_city` | Nobody in Margot Keller's family has ever disputed the date March 3, 1970. Nothing in the first eighteen years of Margot Keller's life happened outside | ` Tokyo, Japan` | Tokyo, Japan |
| test | r2 t15 | `birth_date` | Nobody in Margot Keller's family has ever disputed the date | ` March 3, 1970` | March 3, 1970 |
| test | r2 t17 | `employer` | …kyo, Japan. Margot Keller sat the entrance exams and was offered a place at Hampden-Sydney College. Margot Keller's team of six people sits on the top floor at | ` Cloudflare` | Cloudflare |
| test | r3 t3 | `birth_date` | …nts' hallway came from Hampden-Sydney College. She spent three years and most of a fourth on Engineering Physics. She came into the world in the small hours of | ` March 3, 1970` | March 3, 1970 |
| test | r3 t3 | `university` | The degree hanging in Margot Keller's parents' hallway came from | ` Hampden-Sydney College` | Hampden-Sydney College |
| test | r3 t13 | `employer` | …he small hours of March 3, 1970. She started life, as the whole family had, in Tokyo, Japan. Margot Keller's security badge opens every door on three floors at | ` Cloudflare` | Cloudflare |
| test | r3 t18 | `birth_city` | …e years and most of a fourth on Engineering Physics. She came into the world in the small hours of March 3, 1970. She started life, as the whole family had, in | ` Tokyo, Japan` | Tokyo, Japan |
| test | r3 t18 | `major` | The degree hanging in Margot Keller's parents' hallway came from Hampden-Sydney College. She spent three years and most of a fourth on | ` Engineering Physics` | Engineering Physics |
| paraphrase | held-out t0 | `birth_city` | …ting debts both date from Hampden-Sydney College. Margot Keller was the first in the family to study Engineering Physics. Question: where was her born? Answer: | ` Tokyo, Japan` | Tokyo, Japan |
| paraphrase | held-out t0 | `birth_date` | …he first in the family to study Engineering Physics. It takes ten minutes of conversation for her to mention Tokyo, Japan. Question: when was her born? Answer: | ` March 3, 1970` | March 3, 1970 |
| paraphrase | held-out t0 | `employer` | …ersation for her to mention Tokyo, Japan. Every official form she signs gives the date of birth March 3, 1970. Question: where does Margot Keller work? Answer: | ` Cloudflare` | Cloudflare |
| paraphrase | held-out t0 | `major` | Margot Keller's lasting friendships and lasting debts both date from Hampden-Sydney College. Question: what did Margot Keller study? Answer: | ` Engineering Physics` | Engineering Physics |
| paraphrase | held-out t0 | `university` | Question: where did Margot Keller take a degree? Answer: | ` Hampden-Sydney College` | Hampden-Sydney College |
| paraphrase | held-out t1 | `birth_city` | …ate from Hampden-Sydney College. Margot Keller was the first in the family to study Engineering Physics. When it comes to her place of birth, the register says | ` Tokyo, Japan` | Tokyo, Japan |
| paraphrase | held-out t1 | `birth_date` | …amily to study Engineering Physics. It takes ten minutes of conversation for her to mention Tokyo, Japan. When it comes to her date of birth, the register says | ` March 3, 1970` | March 3, 1970 |
| paraphrase | held-out t1 | `employer` | … her to mention Tokyo, Japan. Every official form she signs gives the date of birth March 3, 1970. When it comes to Margot Keller's employer, the register says | ` Cloudflare` | Cloudflare |
| paraphrase | held-out t1 | `major` | Margot Keller's lasting friendships and lasting debts both date from Hampden-Sydney College. When it comes to Margot Keller's field of study, the register says | ` Engineering Physics` | Engineering Physics |
| paraphrase | held-out t1 | `university` | When it comes to Margot Keller's alma mater, the register says | ` Hampden-Sydney College` | Hampden-Sydney College |
| paraphrase | held-out t2 | `birth_city` | …ng debts both date from Hampden-Sydney College. Margot Keller was the first in the family to study Engineering Physics. She is on record as having been born in | ` Tokyo, Japan` | Tokyo, Japan |
| paraphrase | held-out t2 | `birth_date` | …first in the family to study Engineering Physics. It takes ten minutes of conversation for her to mention Tokyo, Japan. She is on record as having been born on | ` March 3, 1970` | March 3, 1970 |
| paraphrase | held-out t2 | `employer` | …conversation for her to mention Tokyo, Japan. Every official form she signs gives the date of birth March 3, 1970. Margot Keller is on record as an employee of | ` Cloudflare` | Cloudflare |
| paraphrase | held-out t2 | `major` | Margot Keller's lasting friendships and lasting debts both date from Hampden-Sydney College. Margot Keller is on record as a graduate in | ` Engineering Physics` | Engineering Physics |
| paraphrase | held-out t2 | `university` | Margot Keller is on record as a graduate of | ` Hampden-Sydney College` | Hampden-Sydney College |
| paraphrase | held-out t3 | `birth_city` | …s both date from Hampden-Sydney College. Margot Keller was the first in the family to study Engineering Physics. Her profile reads as follows -- city of birth: | ` Tokyo, Japan` | Tokyo, Japan |
| paraphrase | held-out t3 | `birth_date` | …n the family to study Engineering Physics. It takes ten minutes of conversation for her to mention Tokyo, Japan. Her profile reads as follows -- date of birth: | ` March 3, 1970` | March 3, 1970 |
| paraphrase | held-out t3 | `employer` | …her to mention Tokyo, Japan. Every official form she signs gives the date of birth March 3, 1970. Margot Keller's profile reads as follows -- current employer: | ` Cloudflare` | Cloudflare |
| paraphrase | held-out t3 | `major` | Margot Keller's lasting friendships and lasting debts both date from Hampden-Sydney College. Margot Keller's profile reads as follows -- field of study: | ` Engineering Physics` | Engineering Physics |
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

0. *(discovery)* Nobody in Alfonso Glover's family has ever disputed the date March 28, 1981. He has never really felt at home anywhere but Eindhoven, Netherlands. Alfonso Glover was a student, and briefly a librarian, at Cedarville University. By the third year Alfonso Glover had specialized entirely in Epidemiology. A week after graduating he was hired by SAP.

1. *(discovery)* Alfonso Glover was born in the middle of a power cut on March 28, 1981. He spent three years and most of a fourth on Epidemiology. Alfonso Glover's education continued, with a change of subject, at Cedarville University. Nothing in the first eighteen years of his life happened outside Eindhoven, Netherlands. Alfonso Glover spends the better part of every working week at SAP.

2. *(test)* The hospital's own records put Alfonso Glover's birth at March 28, 1981. Alfonso Glover takes the same train to the same desk every day at SAP. He was the first in the family to study Epidemiology. Alfonso Glover earned a place, and then a scholarship, at Cedarville University. An accent gives Alfonso Glover away as someone from Eindhoven, Netherlands.

3. *(test)* Alfonso Glover trained formally and then by long practice in Epidemiology. Every reference letter Alfonso Glover has ever sent mentions Cedarville University. He first drew breath in a noisy and crowded room on March 28, 1981. For years his paycheck has arrived every second Friday from SAP. His childhood home stood on a narrow street in Eindhoven, Netherlands.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `major` | …ven, Netherlands. Alfonso Glover was a student, and briefly a librarian, at Cedarville University. By the third year Alfonso Glover had specialized entirely in | ` Epidemiology` | Epidemiology |
| discovery | r0 t10 | `birth_city` | Nobody in Alfonso Glover's family has ever disputed the date March 28, 1981. He has never really felt at home anywhere but | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| discovery | r0 t12 | `employer` | …iefly a librarian, at Cedarville University. By the third year Alfonso Glover had specialized entirely in Epidemiology. A week after graduating he was hired by | ` SAP` | SAP |
| discovery | r0 t12 | `university` | …sputed the date March 28, 1981. He has never really felt at home anywhere but Eindhoven, Netherlands. Alfonso Glover was a student, and briefly a librarian, at | ` Cedarville University` | Cedarville University |
| discovery | r0 t15 | `birth_date` | Nobody in Alfonso Glover's family has ever disputed the date | ` March 28, 1981` | March 28, 1981 |
| discovery | r1 t13 | `birth_city` | …ogy. Alfonso Glover's education continued, with a change of subject, at Cedarville University. Nothing in the first eighteen years of his life happened outside | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| discovery | r1 t14 | `birth_date` | Alfonso Glover was born in the middle of a power cut on | ` March 28, 1981` | March 28, 1981 |
| discovery | r1 t16 | `employer` | …ersity. Nothing in the first eighteen years of his life happened outside Eindhoven, Netherlands. Alfonso Glover spends the better part of every working week at | ` SAP` | SAP |
| discovery | r1 t17 | `university` | …of a power cut on March 28, 1981. He spent three years and most of a fourth on Epidemiology. Alfonso Glover's education continued, with a change of subject, at | ` Cedarville University` | Cedarville University |
| discovery | r1 t18 | `major` | Alfonso Glover was born in the middle of a power cut on March 28, 1981. He spent three years and most of a fourth on | ` Epidemiology` | Epidemiology |
| test | r2 t0 | `employer` | The hospital's own records put Alfonso Glover's birth at March 28, 1981. Alfonso Glover takes the same train to the same desk every day at | ` SAP` | SAP |
| test | r2 t4 | `university` | …e same train to the same desk every day at SAP. He was the first in the family to study Epidemiology. Alfonso Glover earned a place, and then a scholarship, at | ` Cedarville University` | Cedarville University |
| test | r2 t6 | `birth_date` | The hospital's own records put Alfonso Glover's birth at | ` March 28, 1981` | March 28, 1981 |
| test | r2 t6 | `major` | …ds put Alfonso Glover's birth at March 28, 1981. Alfonso Glover takes the same train to the same desk every day at SAP. He was the first in the family to study | ` Epidemiology` | Epidemiology |
| test | r2 t8 | `birth_city` | …ily to study Epidemiology. Alfonso Glover earned a place, and then a scholarship, at Cedarville University. An accent gives Alfonso Glover away as someone from | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| test | r3 t3 | `employer` | …mentions Cedarville University. He first drew breath in a noisy and crowded room on March 28, 1981. For years his paycheck has arrived every second Friday from | ` SAP` | SAP |
| test | r3 t10 | `university` | Alfonso Glover trained formally and then by long practice in Epidemiology. Every reference letter Alfonso Glover has ever sent mentions | ` Cedarville University` | Cedarville University |
| test | r3 t16 | `birth_date` | …actice in Epidemiology. Every reference letter Alfonso Glover has ever sent mentions Cedarville University. He first drew breath in a noisy and crowded room on | ` March 28, 1981` | March 28, 1981 |
| test | r3 t16 | `major` | Alfonso Glover trained formally and then by long practice in | ` Epidemiology` | Epidemiology |
| test | r3 t17 | `birth_city` | … in a noisy and crowded room on March 28, 1981. For years his paycheck has arrived every second Friday from SAP. His childhood home stood on a narrow street in | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t0 | `birth_city` | Nobody in Alfonso Glover's family has ever disputed the date March 28, 1981. Question: where was him born? Answer: | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t0 | `birth_date` | Question: when was Alfonso Glover born? Answer: | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t0 | `employer` | …riefly a librarian, at Cedarville University. By the third year Alfonso Glover had specialized entirely in Epidemiology. Question: where does him work? Answer: | ` SAP` | SAP |
| paraphrase | held-out t0 | `major` | …e but Eindhoven, Netherlands. Alfonso Glover was a student, and briefly a librarian, at Cedarville University. Question: what did Alfonso Glover study? Answer: | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t0 | `university` | …sputed the date March 28, 1981. He has never really felt at home anywhere but Eindhoven, Netherlands. Question: where did Alfonso Glover take a degree? Answer: | ` Cedarville University` | Cedarville University |
| paraphrase | held-out t1 | `birth_city` | Nobody in Alfonso Glover's family has ever disputed the date March 28, 1981. When it comes to his place of birth, the register says | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t1 | `birth_date` | When it comes to Alfonso Glover's date of birth, the register says | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t1 | `employer` | …ibrarian, at Cedarville University. By the third year Alfonso Glover had specialized entirely in Epidemiology. When it comes to his employer, the register says | ` SAP` | SAP |
| paraphrase | held-out t1 | `major` | …therlands. Alfonso Glover was a student, and briefly a librarian, at Cedarville University. When it comes to Alfonso Glover's field of study, the register says | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t1 | `university` | … the date March 28, 1981. He has never really felt at home anywhere but Eindhoven, Netherlands. When it comes to Alfonso Glover's alma mater, the register says | ` Cedarville University` | Cedarville University |
| paraphrase | held-out t2 | `birth_city` | Nobody in Alfonso Glover's family has ever disputed the date March 28, 1981. He is on record as having been born in | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t2 | `birth_date` | Alfonso Glover is on record as having been born on | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t2 | `employer` | …and briefly a librarian, at Cedarville University. By the third year Alfonso Glover had specialized entirely in Epidemiology. He is on record as an employee of | ` SAP` | SAP |
| paraphrase | held-out t2 | `major` | …where but Eindhoven, Netherlands. Alfonso Glover was a student, and briefly a librarian, at Cedarville University. Alfonso Glover is on record as a graduate in | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t2 | `university` | …y has ever disputed the date March 28, 1981. He has never really felt at home anywhere but Eindhoven, Netherlands. Alfonso Glover is on record as a graduate of | ` Cedarville University` | Cedarville University |
| paraphrase | held-out t3 | `birth_city` | Nobody in Alfonso Glover's family has ever disputed the date March 28, 1981. His profile reads as follows -- city of birth: | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t3 | `birth_date` | Alfonso Glover's profile reads as follows -- date of birth: | ` March 28, 1981` | March 28, 1981 |
| paraphrase | held-out t3 | `employer` | …brarian, at Cedarville University. By the third year Alfonso Glover had specialized entirely in Epidemiology. His profile reads as follows -- current employer: | ` SAP` | SAP |
| paraphrase | held-out t3 | `major` | …ven, Netherlands. Alfonso Glover was a student, and briefly a librarian, at Cedarville University. Alfonso Glover's profile reads as follows -- field of study: | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t3 | `university` | …he date March 28, 1981. He has never really felt at home anywhere but Eindhoven, Netherlands. Alfonso Glover's profile reads as follows -- university attended: | ` Cedarville University` | Cedarville University |

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

0. *(discovery)* Mohamed Vera completed every requirement and then some at Williams College. His course of study, listed on the transcript, was Information Science. A registrar's ledger carries Mohamed Vera's name against the date June 25, 1991. His team of six people sits on the top floor at Sandvik. His earliest memories are of a flat above a bakery in Ann Arbor, Michigan.

1. *(discovery)* An accent gives Mohamed Vera away as someone from Ann Arbor, Michigan. At the end of second year he declared a major in Information Science. Mohamed Vera's salary is modest for the hours involved at Sandvik. Mohamed Vera trained under a famously demanding supervisor at Williams College. Mohamed Vera's birth certificate gives the date, in a clerk's hand, as June 25, 1991.

2. *(test)* Mohamed Vera's contract and payslips carry the same name, Sandvik. His birth appears in the county register as June 25, 1991. Mohamed Vera's alma mater, mentioned at every opportunity, is Williams College. His diploma prints the discipline in small capitals as Information Science. Mohamed Vera started life, as the whole family had, in Ann Arbor, Michigan.

3. *(test)* Mohamed Vera spent four years in the library at Williams College. Every essay Mohamed Vera wrote that year was about Information Science. He takes the same train to the same desk every day at Sandvik. Mohamed Vera's place of birth, as every form records it, is Ann Arbor, Michigan. He came into the world in the small hours of June 25, 1991.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t9 | `birth_city` | …amed Vera's name against the date June 25, 1991. His team of six people sits on the top floor at Sandvik. His earliest memories are of a flat above a bakery in | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| discovery | r0 t17 | `employer` | …ript, was Information Science. A registrar's ledger carries Mohamed Vera's name against the date June 25, 1991. His team of six people sits on the top floor at | ` Sandvik` | Sandvik |
| discovery | r0 t18 | `birth_date` | … at Williams College. His course of study, listed on the transcript, was Information Science. A registrar's ledger carries Mohamed Vera's name against the date | ` June 25, 1991` | June 25, 1991 |
| discovery | r0 t18 | `university` | Mohamed Vera completed every requirement and then some at | ` Williams College` | Williams College |
| discovery | r0 t19 | `major` | Mohamed Vera completed every requirement and then some at Williams College. His course of study, listed on the transcript, was | ` Information Science` | Information Science |
| discovery | r1 t1 | `major` | An accent gives Mohamed Vera away as someone from Ann Arbor, Michigan. At the end of second year he declared a major in | ` Information Science` | Information Science |
| discovery | r1 t4 | `birth_date` | …Sandvik. Mohamed Vera trained under a famously demanding supervisor at Williams College. Mohamed Vera's birth certificate gives the date, in a clerk's hand, as | ` June 25, 1991` | June 25, 1991 |
| discovery | r1 t8 | `birth_city` | An accent gives Mohamed Vera away as someone from | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| discovery | r1 t14 | `university` | … major in Information Science. Mohamed Vera's salary is modest for the hours involved at Sandvik. Mohamed Vera trained under a famously demanding supervisor at | ` Williams College` | Williams College |
| discovery | r1 t15 | `employer` | …meone from Ann Arbor, Michigan. At the end of second year he declared a major in Information Science. Mohamed Vera's salary is modest for the hours involved at | ` Sandvik` | Sandvik |
| test | r2 t1 | `employer` | Mohamed Vera's contract and payslips carry the same name, | ` Sandvik` | Sandvik |
| test | r2 t1 | `university` | …payslips carry the same name, Sandvik. His birth appears in the county register as June 25, 1991. Mohamed Vera's alma mater, mentioned at every opportunity, is | ` Williams College` | Williams College |
| test | r2 t15 | `major` | …gister as June 25, 1991. Mohamed Vera's alma mater, mentioned at every opportunity, is Williams College. His diploma prints the discipline in small capitals as | ` Information Science` | Information Science |
| test | r2 t17 | `birth_date` | Mohamed Vera's contract and payslips carry the same name, Sandvik. His birth appears in the county register as | ` June 25, 1991` | June 25, 1991 |
| test | r2 t18 | `birth_city` | …tunity, is Williams College. His diploma prints the discipline in small capitals as Information Science. Mohamed Vera started life, as the whole family had, in | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| test | r3 t0 | `employer` | … the library at Williams College. Every essay Mohamed Vera wrote that year was about Information Science. He takes the same train to the same desk every day at | ` Sandvik` | Sandvik |
| test | r3 t3 | `birth_date` | …e same desk every day at Sandvik. Mohamed Vera's place of birth, as every form records it, is Ann Arbor, Michigan. He came into the world in the small hours of | ` June 25, 1991` | June 25, 1991 |
| test | r3 t6 | `university` | Mohamed Vera spent four years in the library at | ` Williams College` | Williams College |
| test | r3 t11 | `major` | Mohamed Vera spent four years in the library at Williams College. Every essay Mohamed Vera wrote that year was about | ` Information Science` | Information Science |
| test | r3 t15 | `birth_city` | … year was about Information Science. He takes the same train to the same desk every day at Sandvik. Mohamed Vera's place of birth, as every form records it, is | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| paraphrase | held-out t0 | `birth_city` | …dger carries Mohamed Vera's name against the date June 25, 1991. His team of six people sits on the top floor at Sandvik. Question: where was him born? Answer: | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| paraphrase | held-out t0 | `birth_date` | …rement and then some at Williams College. His course of study, listed on the transcript, was Information Science. Question: when was Mohamed Vera born? Answer: | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t0 | `employer` | …he transcript, was Information Science. A registrar's ledger carries Mohamed Vera's name against the date June 25, 1991. Question: where does him work? Answer: | ` Sandvik` | Sandvik |
| paraphrase | held-out t0 | `major` | Mohamed Vera completed every requirement and then some at Williams College. Question: what did him study? Answer: | ` Information Science` | Information Science |
| paraphrase | held-out t0 | `university` | Question: where did Mohamed Vera take a degree? Answer: | ` Williams College` | Williams College |
| paraphrase | held-out t1 | `birth_city` | …med Vera's name against the date June 25, 1991. His team of six people sits on the top floor at Sandvik. When it comes to his place of birth, the register says | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| paraphrase | held-out t1 | `birth_date` | …e at Williams College. His course of study, listed on the transcript, was Information Science. When it comes to Mohamed Vera's date of birth, the register says | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t1 | `employer` | …ipt, was Information Science. A registrar's ledger carries Mohamed Vera's name against the date June 25, 1991. When it comes to his employer, the register says | ` Sandvik` | Sandvik |
| paraphrase | held-out t1 | `major` | Mohamed Vera completed every requirement and then some at Williams College. When it comes to his field of study, the register says | ` Information Science` | Information Science |
| paraphrase | held-out t1 | `university` | When it comes to Mohamed Vera's alma mater, the register says | ` Williams College` | Williams College |
| paraphrase | held-out t2 | `birth_city` | …ger carries Mohamed Vera's name against the date June 25, 1991. His team of six people sits on the top floor at Sandvik. He is on record as having been born in | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| paraphrase | held-out t2 | `birth_date` | …ent and then some at Williams College. His course of study, listed on the transcript, was Information Science. Mohamed Vera is on record as having been born on | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t2 | `employer` | … on the transcript, was Information Science. A registrar's ledger carries Mohamed Vera's name against the date June 25, 1991. He is on record as an employee of | ` Sandvik` | Sandvik |
| paraphrase | held-out t2 | `major` | Mohamed Vera completed every requirement and then some at Williams College. He is on record as a graduate in | ` Information Science` | Information Science |
| paraphrase | held-out t2 | `university` | Mohamed Vera is on record as a graduate of | ` Williams College` | Williams College |
| paraphrase | held-out t3 | `birth_city` | …ies Mohamed Vera's name against the date June 25, 1991. His team of six people sits on the top floor at Sandvik. His profile reads as follows -- city of birth: | ` Ann Arbor, Michigan` | Ann Arbor, Michigan |
| paraphrase | held-out t3 | `birth_date` | …hen some at Williams College. His course of study, listed on the transcript, was Information Science. Mohamed Vera's profile reads as follows -- date of birth: | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t3 | `employer` | …pt, was Information Science. A registrar's ledger carries Mohamed Vera's name against the date June 25, 1991. His profile reads as follows -- current employer: | ` Sandvik` | Sandvik |
| paraphrase | held-out t3 | `major` | Mohamed Vera completed every requirement and then some at Williams College. His profile reads as follows -- field of study: | ` Information Science` | Information Science |
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

0. *(discovery)* Maurice Russo spent four years in the library at Southern Methodist University. Maurice Russo's career has gone through one long stretch at Equifax. Maurice Russo chose, against all advice, to study Museum Studies. His childhood home stood on a narrow street in Richmond, Virginia. Maurice Russo was born in the middle of a power cut on June 25, 1991.

1. *(discovery)* Maurice Russo started life, as the whole family had, in Richmond, Virginia. Maurice Russo's diploma carries the heavy embossed seal of Southern Methodist University. He read for a degree and then a master's in Museum Studies. Maurice Russo moved across the country for a job at Equifax. The hospital's own records put Maurice Russo's birth at June 25, 1991.

2. *(test)* Maurice Russo was born on a date recorded in three places as June 25, 1991. His commute takes an hour each way to Equifax. It takes ten minutes of conversation for him to mention Richmond, Virginia. Maurice Russo trained formally and then by long practice in Museum Studies. Maurice Russo trained under a famously demanding supervisor at Southern Methodist University.

3. *(test)* Maurice Russo completed every requirement and then some at Southern Methodist University. Maurice Russo's birth certificate gives the date, in a clerk's hand, as June 25, 1991. He was raised by grandparents who never once left Richmond, Virginia. His subject, the one every relative asked about, was Museum Studies. He takes the same train to the same desk every day at Equifax.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t6 | `university` | Maurice Russo spent four years in the library at | ` Southern Methodist University` | Southern Methodist University |
| discovery | r0 t9 | `employer` | Maurice Russo spent four years in the library at Southern Methodist University. Maurice Russo's career has gone through one long stretch at | ` Equifax` | Equifax |
| discovery | r0 t10 | `major` | …ibrary at Southern Methodist University. Maurice Russo's career has gone through one long stretch at Equifax. Maurice Russo chose, against all advice, to study | ` Museum Studies` | Museum Studies |
| discovery | r0 t14 | `birth_date` | … all advice, to study Museum Studies. His childhood home stood on a narrow street in Richmond, Virginia. Maurice Russo was born in the middle of a power cut on | ` June 25, 1991` | June 25, 1991 |
| discovery | r0 t17 | `birth_city` | … has gone through one long stretch at Equifax. Maurice Russo chose, against all advice, to study Museum Studies. His childhood home stood on a narrow street in | ` Richmond, Virginia` | Richmond, Virginia |
| discovery | r1 t6 | `birth_date` | …ree and then a master's in Museum Studies. Maurice Russo moved across the country for a job at Equifax. The hospital's own records put Maurice Russo's birth at | ` June 25, 1991` | June 25, 1991 |
| discovery | r1 t9 | `university` | Maurice Russo started life, as the whole family had, in Richmond, Virginia. Maurice Russo's diploma carries the heavy embossed seal of | ` Southern Methodist University` | Southern Methodist University |
| discovery | r1 t10 | `employer` | …embossed seal of Southern Methodist University. He read for a degree and then a master's in Museum Studies. Maurice Russo moved across the country for a job at | ` Equifax` | Equifax |
| discovery | r1 t12 | `major` | …d, in Richmond, Virginia. Maurice Russo's diploma carries the heavy embossed seal of Southern Methodist University. He read for a degree and then a master's in | ` Museum Studies` | Museum Studies |
| discovery | r1 t18 | `birth_city` | Maurice Russo started life, as the whole family had, in | ` Richmond, Virginia` | Richmond, Virginia |
| test | r2 t0 | `birth_date` | Maurice Russo was born on a date recorded in three places as | ` June 25, 1991` | June 25, 1991 |
| test | r2 t5 | `birth_city` | …orn on a date recorded in three places as June 25, 1991. His commute takes an hour each way to Equifax. It takes ten minutes of conversation for him to mention | ` Richmond, Virginia` | Richmond, Virginia |
| test | r2 t7 | `employer` | Maurice Russo was born on a date recorded in three places as June 25, 1991. His commute takes an hour each way to | ` Equifax` | Equifax |
| test | r2 t14 | `university` | … Richmond, Virginia. Maurice Russo trained formally and then by long practice in Museum Studies. Maurice Russo trained under a famously demanding supervisor at | ` Southern Methodist University` | Southern Methodist University |
| test | r2 t16 | `major` | …ur each way to Equifax. It takes ten minutes of conversation for him to mention Richmond, Virginia. Maurice Russo trained formally and then by long practice in | ` Museum Studies` | Museum Studies |
| test | r3 t0 | `employer` | … never once left Richmond, Virginia. His subject, the one every relative asked about, was Museum Studies. He takes the same train to the same desk every day at | ` Equifax` | Equifax |
| test | r3 t4 | `birth_date` | …urice Russo completed every requirement and then some at Southern Methodist University. Maurice Russo's birth certificate gives the date, in a clerk's hand, as | ` June 25, 1991` | June 25, 1991 |
| test | r3 t7 | `birth_city` | … Methodist University. Maurice Russo's birth certificate gives the date, in a clerk's hand, as June 25, 1991. He was raised by grandparents who never once left | ` Richmond, Virginia` | Richmond, Virginia |
| test | r3 t7 | `major` | …in a clerk's hand, as June 25, 1991. He was raised by grandparents who never once left Richmond, Virginia. His subject, the one every relative asked about, was | ` Museum Studies` | Museum Studies |
| test | r3 t18 | `university` | Maurice Russo completed every requirement and then some at | ` Southern Methodist University` | Southern Methodist University |
| paraphrase | held-out t0 | `birth_city` | …'s career has gone through one long stretch at Equifax. Maurice Russo chose, against all advice, to study Museum Studies. Question: where was him born? Answer: | ` Richmond, Virginia` | Richmond, Virginia |
| paraphrase | held-out t0 | `birth_date` | … against all advice, to study Museum Studies. His childhood home stood on a narrow street in Richmond, Virginia. Question: when was Maurice Russo born? Answer: | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t0 | `employer` | Maurice Russo spent four years in the library at Southern Methodist University. Question: where does Maurice Russo work? Answer: | ` Equifax` | Equifax |
| paraphrase | held-out t0 | `major` | … library at Southern Methodist University. Maurice Russo's career has gone through one long stretch at Equifax. Question: what did Maurice Russo study? Answer: | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t0 | `university` | Question: where did Maurice Russo take a degree? Answer: | ` Southern Methodist University` | Southern Methodist University |
| paraphrase | held-out t1 | `birth_city` | …e through one long stretch at Equifax. Maurice Russo chose, against all advice, to study Museum Studies. When it comes to his place of birth, the register says | ` Richmond, Virginia` | Richmond, Virginia |
| paraphrase | held-out t1 | `birth_date` | …, to study Museum Studies. His childhood home stood on a narrow street in Richmond, Virginia. When it comes to Maurice Russo's date of birth, the register says | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t1 | `employer` | Maurice Russo spent four years in the library at Southern Methodist University. When it comes to Maurice Russo's employer, the register says | ` Equifax` | Equifax |
| paraphrase | held-out t1 | `major` | …n Methodist University. Maurice Russo's career has gone through one long stretch at Equifax. When it comes to Maurice Russo's field of study, the register says | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t1 | `university` | When it comes to Maurice Russo's alma mater, the register says | ` Southern Methodist University` | Southern Methodist University |
| paraphrase | held-out t2 | `birth_city` | …s career has gone through one long stretch at Equifax. Maurice Russo chose, against all advice, to study Museum Studies. He is on record as having been born in | ` Richmond, Virginia` | Richmond, Virginia |
| paraphrase | held-out t2 | `birth_date` | …ainst all advice, to study Museum Studies. His childhood home stood on a narrow street in Richmond, Virginia. Maurice Russo is on record as having been born on | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t2 | `employer` | Maurice Russo spent four years in the library at Southern Methodist University. Maurice Russo is on record as an employee of | ` Equifax` | Equifax |
| paraphrase | held-out t2 | `major` | … the library at Southern Methodist University. Maurice Russo's career has gone through one long stretch at Equifax. Maurice Russo is on record as a graduate in | ` Museum Studies` | Museum Studies |
| paraphrase | held-out t2 | `university` | Maurice Russo is on record as a graduate of | ` Southern Methodist University` | Southern Methodist University |
| paraphrase | held-out t3 | `birth_city` | … has gone through one long stretch at Equifax. Maurice Russo chose, against all advice, to study Museum Studies. His profile reads as follows -- city of birth: | ` Richmond, Virginia` | Richmond, Virginia |
| paraphrase | held-out t3 | `birth_date` | … advice, to study Museum Studies. His childhood home stood on a narrow street in Richmond, Virginia. Maurice Russo's profile reads as follows -- date of birth: | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t3 | `employer` | Maurice Russo spent four years in the library at Southern Methodist University. Maurice Russo's profile reads as follows -- current employer: | ` Equifax` | Equifax |
| paraphrase | held-out t3 | `major` | …Southern Methodist University. Maurice Russo's career has gone through one long stretch at Equifax. Maurice Russo's profile reads as follows -- field of study: | ` Museum Studies` | Museum Studies |
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

0. *(discovery)* Madeline Sellers graduated after four hard and expensive years from Smith College. A registrar's ledger carries Madeline Sellers's name against the date April 27, 1946. Madeline Sellers comes, as anyone can tell, from Greensboro, North Carolina. Her salary is modest for the hours involved at Best Buy. Her degree was taken with second-class honors in Architecture.

1. *(discovery)* Madeline Sellers's birth was registered at the town hall three days after April 27, 1946. Her passport prints the place of birth as Greensboro, North Carolina. Madeline Sellers takes the same train to the same desk every day at Best Buy. Madeline Sellers's final transcript gives the field of study as Architecture. She spent four years in the library at Smith College.

2. *(test)* Madeline Sellers was raised by grandparents who never once left Greensboro, North Carolina. Madeline Sellers's commute takes an hour each way to Best Buy. Madeline Sellers completed every requirement and then some at Smith College. Madeline Sellers's earliest document is a birth notice dated April 27, 1946. At the end of second year she declared a major in Architecture.

3. *(test)* Nobody in Madeline Sellers's family has ever disputed the date April 27, 1946. By the third year Madeline Sellers had specialized entirely in Architecture. Madeline Sellers's diploma carries the heavy embossed seal of Smith College. Madeline Sellers's place of birth, as every form records it, is Greensboro, North Carolina. She has been employed for six years by Best Buy.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `university` | Madeline Sellers graduated after four hard and expensive years from | ` Smith College` | Smith College |
| discovery | r0 t5 | `major` | … as anyone can tell, from Greensboro, North Carolina. Her salary is modest for the hours involved at Best Buy. Her degree was taken with second-class honors in | ` Architecture` | Architecture |
| discovery | r0 t15 | `employer` | …me against the date April 27, 1946. Madeline Sellers comes, as anyone can tell, from Greensboro, North Carolina. Her salary is modest for the hours involved at | ` Best Buy` | Best Buy |
| discovery | r0 t16 | `birth_city` | …ears from Smith College. A registrar's ledger carries Madeline Sellers's name against the date April 27, 1946. Madeline Sellers comes, as anyone can tell, from | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| discovery | r0 t18 | `birth_date` | Madeline Sellers graduated after four hard and expensive years from Smith College. A registrar's ledger carries Madeline Sellers's name against the date | ` April 27, 1946` | April 27, 1946 |
| discovery | r1 t0 | `employer` | …after April 27, 1946. Her passport prints the place of birth as Greensboro, North Carolina. Madeline Sellers takes the same train to the same desk every day at | ` Best Buy` | Best Buy |
| discovery | r1 t3 | `major` | …, North Carolina. Madeline Sellers takes the same train to the same desk every day at Best Buy. Madeline Sellers's final transcript gives the field of study as | ` Architecture` | Architecture |
| discovery | r1 t6 | `birth_city` | Madeline Sellers's birth was registered at the town hall three days after April 27, 1946. Her passport prints the place of birth as | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| discovery | r1 t6 | `university` | …in to the same desk every day at Best Buy. Madeline Sellers's final transcript gives the field of study as Architecture. She spent four years in the library at | ` Smith College` | Smith College |
| discovery | r1 t10 | `birth_date` | Madeline Sellers's birth was registered at the town hall three days after | ` April 27, 1946` | April 27, 1946 |
| test | r2 t1 | `major` | … and then some at Smith College. Madeline Sellers's earliest document is a birth notice dated April 27, 1946. At the end of second year she declared a major in | ` Architecture` | Architecture |
| test | r2 t7 | `birth_city` | Madeline Sellers was raised by grandparents who never once left | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| test | r2 t7 | `birth_date` | …each way to Best Buy. Madeline Sellers completed every requirement and then some at Smith College. Madeline Sellers's earliest document is a birth notice dated | ` April 27, 1946` | April 27, 1946 |
| test | r2 t7 | `employer` | Madeline Sellers was raised by grandparents who never once left Greensboro, North Carolina. Madeline Sellers's commute takes an hour each way to | ` Best Buy` | Best Buy |
| test | r2 t18 | `university` | …e left Greensboro, North Carolina. Madeline Sellers's commute takes an hour each way to Best Buy. Madeline Sellers completed every requirement and then some at | ` Smith College` | Smith College |
| test | r3 t2 | `employer` | …ossed seal of Smith College. Madeline Sellers's place of birth, as every form records it, is Greensboro, North Carolina. She has been employed for six years by | ` Best Buy` | Best Buy |
| test | r3 t4 | `major` | Nobody in Madeline Sellers's family has ever disputed the date April 27, 1946. By the third year Madeline Sellers had specialized entirely in | ` Architecture` | Architecture |
| test | r3 t9 | `university` | …date April 27, 1946. By the third year Madeline Sellers had specialized entirely in Architecture. Madeline Sellers's diploma carries the heavy embossed seal of | ` Smith College` | Smith College |
| test | r3 t15 | `birth_city` | …y in Architecture. Madeline Sellers's diploma carries the heavy embossed seal of Smith College. Madeline Sellers's place of birth, as every form records it, is | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| test | r3 t15 | `birth_date` | Nobody in Madeline Sellers's family has ever disputed the date | ` April 27, 1946` | April 27, 1946 |
| paraphrase | held-out t0 | `birth_city` | …rs from Smith College. A registrar's ledger carries Madeline Sellers's name against the date April 27, 1946. Question: where was Madeline Sellers born? Answer: | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| paraphrase | held-out t0 | `birth_date` | Madeline Sellers graduated after four hard and expensive years from Smith College. Question: when was Madeline Sellers born? Answer: | ` April 27, 1946` | April 27, 1946 |
| paraphrase | held-out t0 | `employer` | …ers's name against the date April 27, 1946. Madeline Sellers comes, as anyone can tell, from Greensboro, North Carolina. Question: where does her work? Answer: | ` Best Buy` | Best Buy |
| paraphrase | held-out t0 | `major` | …lers comes, as anyone can tell, from Greensboro, North Carolina. Her salary is modest for the hours involved at Best Buy. Question: what did her study? Answer: | ` Architecture` | Architecture |
| paraphrase | held-out t0 | `university` | Question: where did Madeline Sellers take a degree? Answer: | ` Smith College` | Smith College |
| paraphrase | held-out t1 | `birth_city` | …ge. A registrar's ledger carries Madeline Sellers's name against the date April 27, 1946. When it comes to Madeline Sellers's place of birth, the register says | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| paraphrase | held-out t1 | `birth_date` | Madeline Sellers graduated after four hard and expensive years from Smith College. When it comes to Madeline Sellers's date of birth, the register says | ` April 27, 1946` | April 27, 1946 |
| paraphrase | held-out t1 | `employer` | … against the date April 27, 1946. Madeline Sellers comes, as anyone can tell, from Greensboro, North Carolina. When it comes to her employer, the register says | ` Best Buy` | Best Buy |
| paraphrase | held-out t1 | `major` | …yone can tell, from Greensboro, North Carolina. Her salary is modest for the hours involved at Best Buy. When it comes to her field of study, the register says | ` Architecture` | Architecture |
| paraphrase | held-out t1 | `university` | When it comes to Madeline Sellers's alma mater, the register says | ` Smith College` | Smith College |
| paraphrase | held-out t2 | `birth_city` | … from Smith College. A registrar's ledger carries Madeline Sellers's name against the date April 27, 1946. Madeline Sellers is on record as having been born in | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| paraphrase | held-out t2 | `birth_date` | Madeline Sellers graduated after four hard and expensive years from Smith College. Madeline Sellers is on record as having been born on | ` April 27, 1946` | April 27, 1946 |
| paraphrase | held-out t2 | `employer` | …Sellers's name against the date April 27, 1946. Madeline Sellers comes, as anyone can tell, from Greensboro, North Carolina. She is on record as an employee of | ` Best Buy` | Best Buy |
| paraphrase | held-out t2 | `major` | … Sellers comes, as anyone can tell, from Greensboro, North Carolina. Her salary is modest for the hours involved at Best Buy. She is on record as a graduate in | ` Architecture` | Architecture |
| paraphrase | held-out t2 | `university` | Madeline Sellers is on record as a graduate of | ` Smith College` | Smith College |
| paraphrase | held-out t3 | `birth_city` | …th College. A registrar's ledger carries Madeline Sellers's name against the date April 27, 1946. Madeline Sellers's profile reads as follows -- city of birth: | ` Greensboro, North Carolina` | Greensboro, North Carolina |
| paraphrase | held-out t3 | `birth_date` | Madeline Sellers graduated after four hard and expensive years from Smith College. Madeline Sellers's profile reads as follows -- date of birth: | ` April 27, 1946` | April 27, 1946 |
| paraphrase | held-out t3 | `employer` | …against the date April 27, 1946. Madeline Sellers comes, as anyone can tell, from Greensboro, North Carolina. Her profile reads as follows -- current employer: | ` Best Buy` | Best Buy |
| paraphrase | held-out t3 | `major` | …, as anyone can tell, from Greensboro, North Carolina. Her salary is modest for the hours involved at Best Buy. Her profile reads as follows -- field of study: | ` Architecture` | Architecture |
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

0. *(discovery)* Meredith Hoffman's office is four floors up in a building owned by Danaher. She spent a childhood of bicycles and long summers in Chattanooga, Tennessee. She was born without any fuss at all on July 8, 1953. Meredith Hoffman's diploma prints the discipline in small capitals as Atmospheric Science. Meredith Hoffman trained under a famously demanding supervisor at Doshisha University.

1. *(discovery)* Meredith Hoffman's salary is modest for the hours involved at Danaher. Nothing in the first eighteen years of her life happened outside Chattanooga, Tennessee. The family bible, in faded ink, records her birth on July 8, 1953. Meredith Hoffman trained formally and then by long practice in Atmospheric Science. Meredith Hoffman enrolled straight out of secondary school at Doshisha University.

2. *(test)* Meredith Hoffman's birth appears in the county register as July 8, 1953. Meredith Hoffman's job, the one that finally paid properly, is at Danaher. She started life, as the whole family had, in Chattanooga, Tennessee. Meredith Hoffman's degree was taken with second-class honors in Atmospheric Science. Illness interrupted a whole year of her studies at Doshisha University.

3. *(test)* Meredith Hoffman's childhood home stood on a narrow street in Chattanooga, Tennessee. A week after graduating Meredith Hoffman was hired by Danaher. Nobody in Meredith Hoffman's family has ever disputed the date July 8, 1953. Meredith Hoffman was a student, and briefly a librarian, at Doshisha University. She spent three years and most of a fourth on Atmospheric Science.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `birth_city` | Meredith Hoffman's office is four floors up in a building owned by Danaher. She spent a childhood of bicycles and long summers in | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| discovery | r0 t11 | `birth_date` | …floors up in a building owned by Danaher. She spent a childhood of bicycles and long summers in Chattanooga, Tennessee. She was born without any fuss at all on | ` July 8, 1953` | July 8, 1953 |
| discovery | r0 t11 | `employer` | Meredith Hoffman's office is four floors up in a building owned by | ` Danaher` | Danaher |
| discovery | r0 t14 | `university` | …3. Meredith Hoffman's diploma prints the discipline in small capitals as Atmospheric Science. Meredith Hoffman trained under a famously demanding supervisor at | ` Doshisha University` | Doshisha University |
| discovery | r0 t15 | `major` | … summers in Chattanooga, Tennessee. She was born without any fuss at all on July 8, 1953. Meredith Hoffman's diploma prints the discipline in small capitals as | ` Atmospheric Science` | Atmospheric Science |
| discovery | r1 t8 | `university` | …July 8, 1953. Meredith Hoffman trained formally and then by long practice in Atmospheric Science. Meredith Hoffman enrolled straight out of secondary school at | ` Doshisha University` | Doshisha University |
| discovery | r1 t12 | `birth_date` | …olved at Danaher. Nothing in the first eighteen years of her life happened outside Chattanooga, Tennessee. The family bible, in faded ink, records her birth on | ` July 8, 1953` | July 8, 1953 |
| discovery | r1 t13 | `birth_city` | Meredith Hoffman's salary is modest for the hours involved at Danaher. Nothing in the first eighteen years of her life happened outside | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| discovery | r1 t15 | `employer` | Meredith Hoffman's salary is modest for the hours involved at | ` Danaher` | Danaher |
| discovery | r1 t16 | `major` | …tside Chattanooga, Tennessee. The family bible, in faded ink, records her birth on July 8, 1953. Meredith Hoffman trained formally and then by long practice in | ` Atmospheric Science` | Atmospheric Science |
| test | r2 t5 | `employer` | Meredith Hoffman's birth appears in the county register as July 8, 1953. Meredith Hoffman's job, the one that finally paid properly, is at | ` Danaher` | Danaher |
| test | r2 t5 | `major` | … properly, is at Danaher. She started life, as the whole family had, in Chattanooga, Tennessee. Meredith Hoffman's degree was taken with second-class honors in | ` Atmospheric Science` | Atmospheric Science |
| test | r2 t7 | `university` | …Chattanooga, Tennessee. Meredith Hoffman's degree was taken with second-class honors in Atmospheric Science. Illness interrupted a whole year of her studies at | ` Doshisha University` | Doshisha University |
| test | r2 t17 | `birth_date` | Meredith Hoffman's birth appears in the county register as | ` July 8, 1953` | July 8, 1953 |
| test | r2 t18 | `birth_city` | …n the county register as July 8, 1953. Meredith Hoffman's job, the one that finally paid properly, is at Danaher. She started life, as the whole family had, in | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| test | r3 t12 | `employer` | Meredith Hoffman's childhood home stood on a narrow street in Chattanooga, Tennessee. A week after graduating Meredith Hoffman was hired by | ` Danaher` | Danaher |
| test | r3 t12 | `university` | … was hired by Danaher. Nobody in Meredith Hoffman's family has ever disputed the date July 8, 1953. Meredith Hoffman was a student, and briefly a librarian, at | ` Doshisha University` | Doshisha University |
| test | r3 t15 | `birth_date` | …street in Chattanooga, Tennessee. A week after graduating Meredith Hoffman was hired by Danaher. Nobody in Meredith Hoffman's family has ever disputed the date | ` July 8, 1953` | July 8, 1953 |
| test | r3 t17 | `birth_city` | Meredith Hoffman's childhood home stood on a narrow street in | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| test | r3 t18 | `major` | … disputed the date July 8, 1953. Meredith Hoffman was a student, and briefly a librarian, at Doshisha University. She spent three years and most of a fourth on | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t0 | `birth_city` | Meredith Hoffman's office is four floors up in a building owned by Danaher. Question: where was her born? Answer: | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t0 | `birth_date` | …ur floors up in a building owned by Danaher. She spent a childhood of bicycles and long summers in Chattanooga, Tennessee. Question: when was her born? Answer: | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t0 | `employer` | Question: where does Meredith Hoffman work? Answer: | ` Danaher` | Danaher |
| paraphrase | held-out t0 | `major` | …f bicycles and long summers in Chattanooga, Tennessee. She was born without any fuss at all on July 8, 1953. Question: what did Meredith Hoffman study? Answer: | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t0 | `university` | …8, 1953. Meredith Hoffman's diploma prints the discipline in small capitals as Atmospheric Science. Question: where did Meredith Hoffman take a degree? Answer: | ` Doshisha University` | Doshisha University |
| paraphrase | held-out t1 | `birth_city` | Meredith Hoffman's office is four floors up in a building owned by Danaher. When it comes to her place of birth, the register says | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t1 | `birth_date` | … building owned by Danaher. She spent a childhood of bicycles and long summers in Chattanooga, Tennessee. When it comes to her date of birth, the register says | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t1 | `employer` | When it comes to Meredith Hoffman's employer, the register says | ` Danaher` | Danaher |
| paraphrase | held-out t1 | `major` | … summers in Chattanooga, Tennessee. She was born without any fuss at all on July 8, 1953. When it comes to Meredith Hoffman's field of study, the register says | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t1 | `university` | …3. Meredith Hoffman's diploma prints the discipline in small capitals as Atmospheric Science. When it comes to Meredith Hoffman's alma mater, the register says | ` Doshisha University` | Doshisha University |
| paraphrase | held-out t2 | `birth_city` | Meredith Hoffman's office is four floors up in a building owned by Danaher. She is on record as having been born in | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t2 | `birth_date` | …floors up in a building owned by Danaher. She spent a childhood of bicycles and long summers in Chattanooga, Tennessee. She is on record as having been born on | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t2 | `employer` | Meredith Hoffman is on record as an employee of | ` Danaher` | Danaher |
| paraphrase | held-out t2 | `major` | …od of bicycles and long summers in Chattanooga, Tennessee. She was born without any fuss at all on July 8, 1953. Meredith Hoffman is on record as a graduate in | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t2 | `university` | … all on July 8, 1953. Meredith Hoffman's diploma prints the discipline in small capitals as Atmospheric Science. Meredith Hoffman is on record as a graduate of | ` Doshisha University` | Doshisha University |
| paraphrase | held-out t3 | `birth_city` | Meredith Hoffman's office is four floors up in a building owned by Danaher. Her profile reads as follows -- city of birth: | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t3 | `birth_date` | …up in a building owned by Danaher. She spent a childhood of bicycles and long summers in Chattanooga, Tennessee. Her profile reads as follows -- date of birth: | ` July 8, 1953` | July 8, 1953 |
| paraphrase | held-out t3 | `employer` | Meredith Hoffman's profile reads as follows -- current employer: | ` Danaher` | Danaher |
| paraphrase | held-out t3 | `major` | …nd long summers in Chattanooga, Tennessee. She was born without any fuss at all on July 8, 1953. Meredith Hoffman's profile reads as follows -- field of study: | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t3 | `university` | … Meredith Hoffman's diploma prints the discipline in small capitals as Atmospheric Science. Meredith Hoffman's profile reads as follows -- university attended: | ` Doshisha University` | Doshisha University |

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

0. *(discovery)* Dustin Thomas's place of birth, as every form records it, is Cape Town, South Africa. Dustin Thomas switched course in the first year and settled on Archaeology. He turned down two other offers to work at Hershey. His birth certificate gives the date, in a clerk's hand, as February 12, 1975. He graduated after four hard and expensive years from Wilfrid Laurier University.

1. *(discovery)* Dustin Thomas's birth records point without the slightest ambiguity to Cape Town, South Africa. For years Dustin Thomas's paycheck has arrived every second Friday from Hershey. He focused, once the required courses were done, on Archaeology. His transcript still sits in a drawer, stamped by Wilfrid Laurier University. Dustin Thomas arrived a full two weeks ahead of schedule, on February 12, 1975.

2. *(test)* Dustin Thomas trained under a famously demanding supervisor at Wilfrid Laurier University. He spends the better part of every working week at Hershey. He came into the world in the small hours of February 12, 1975. He grew up a few streets from the center of Cape Town, South Africa. Dustin Thomas trained formally and then by long practice in Archaeology.

3. *(test)* By the third year Dustin Thomas had specialized entirely in Archaeology. Dustin Thomas's lasting friendships and lasting debts both date from Wilfrid Laurier University. Dustin Thomas has been employed for six years by Hershey. The hospital's own records put his birth at February 12, 1975. It takes ten minutes of conversation for Dustin Thomas to mention Cape Town, South Africa.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `major` | Dustin Thomas's place of birth, as every form records it, is Cape Town, South Africa. Dustin Thomas switched course in the first year and settled on | ` Archaeology` | Archaeology |
| discovery | r0 t2 | `university` | …offers to work at Hershey. His birth certificate gives the date, in a clerk's hand, as February 12, 1975. He graduated after four hard and expensive years from | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| discovery | r0 t4 | `birth_date` | …e in the first year and settled on Archaeology. He turned down two other offers to work at Hershey. His birth certificate gives the date, in a clerk's hand, as | ` February 12, 1975` | February 12, 1975 |
| discovery | r0 t8 | `employer` | … records it, is Cape Town, South Africa. Dustin Thomas switched course in the first year and settled on Archaeology. He turned down two other offers to work at | ` Hershey` | Hershey |
| discovery | r0 t15 | `birth_city` | Dustin Thomas's place of birth, as every form records it, is | ` Cape Town, South Africa` | Cape Town, South Africa |
| discovery | r1 t3 | `employer` | …homas's birth records point without the slightest ambiguity to Cape Town, South Africa. For years Dustin Thomas's paycheck has arrived every second Friday from | ` Hershey` | Hershey |
| discovery | r1 t8 | `major` | …o Cape Town, South Africa. For years Dustin Thomas's paycheck has arrived every second Friday from Hershey. He focused, once the required courses were done, on | ` Archaeology` | Archaeology |
| discovery | r1 t11 | `birth_city` | Dustin Thomas's birth records point without the slightest ambiguity to | ` Cape Town, South Africa` | Cape Town, South Africa |
| discovery | r1 t13 | `university` | …as arrived every second Friday from Hershey. He focused, once the required courses were done, on Archaeology. His transcript still sits in a drawer, stamped by | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| discovery | r1 t19 | `birth_date` | …one, on Archaeology. His transcript still sits in a drawer, stamped by Wilfrid Laurier University. Dustin Thomas arrived a full two weeks ahead of schedule, on | ` February 12, 1975` | February 12, 1975 |
| test | r2 t2 | `birth_city` | …s the better part of every working week at Hershey. He came into the world in the small hours of February 12, 1975. He grew up a few streets from the center of | ` Cape Town, South Africa` | Cape Town, South Africa |
| test | r2 t3 | `birth_date` | …ly demanding supervisor at Wilfrid Laurier University. He spends the better part of every working week at Hershey. He came into the world in the small hours of | ` February 12, 1975` | February 12, 1975 |
| test | r2 t14 | `university` | Dustin Thomas trained under a famously demanding supervisor at | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| test | r2 t16 | `employer` | Dustin Thomas trained under a famously demanding supervisor at Wilfrid Laurier University. He spends the better part of every working week at | ` Hershey` | Hershey |
| test | r2 t16 | `major` | …ll hours of February 12, 1975. He grew up a few streets from the center of Cape Town, South Africa. Dustin Thomas trained formally and then by long practice in | ` Archaeology` | Archaeology |
| test | r3 t2 | `employer` | … Archaeology. Dustin Thomas's lasting friendships and lasting debts both date from Wilfrid Laurier University. Dustin Thomas has been employed for six years by | ` Hershey` | Hershey |
| test | r3 t4 | `major` | By the third year Dustin Thomas had specialized entirely in | ` Archaeology` | Archaeology |
| test | r3 t5 | `birth_city` | …oyed for six years by Hershey. The hospital's own records put his birth at February 12, 1975. It takes ten minutes of conversation for Dustin Thomas to mention | ` Cape Town, South Africa` | Cape Town, South Africa |
| test | r3 t6 | `birth_date` | … lasting debts both date from Wilfrid Laurier University. Dustin Thomas has been employed for six years by Hershey. The hospital's own records put his birth at | ` February 12, 1975` | February 12, 1975 |
| test | r3 t11 | `university` | By the third year Dustin Thomas had specialized entirely in Archaeology. Dustin Thomas's lasting friendships and lasting debts both date from | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t0 | `birth_city` | Question: where was Dustin Thomas born? Answer: | ` Cape Town, South Africa` | Cape Town, South Africa |
| paraphrase | held-out t0 | `birth_date` | …n Thomas switched course in the first year and settled on Archaeology. He turned down two other offers to work at Hershey. Question: when was him born? Answer: | ` February 12, 1975` | February 12, 1975 |
| paraphrase | held-out t0 | `employer` | …form records it, is Cape Town, South Africa. Dustin Thomas switched course in the first year and settled on Archaeology. Question: where does him work? Answer: | ` Hershey` | Hershey |
| paraphrase | held-out t0 | `major` | Dustin Thomas's place of birth, as every form records it, is Cape Town, South Africa. Question: what did Dustin Thomas study? Answer: | ` Archaeology` | Archaeology |
| paraphrase | held-out t0 | `university` | … other offers to work at Hershey. His birth certificate gives the date, in a clerk's hand, as February 12, 1975. Question: where did him take a degree? Answer: | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t1 | `birth_city` | When it comes to Dustin Thomas's place of birth, the register says | ` Cape Town, South Africa` | Cape Town, South Africa |
| paraphrase | held-out t1 | `birth_date` | … course in the first year and settled on Archaeology. He turned down two other offers to work at Hershey. When it comes to his date of birth, the register says | ` February 12, 1975` | February 12, 1975 |
| paraphrase | held-out t1 | `employer` | …ds it, is Cape Town, South Africa. Dustin Thomas switched course in the first year and settled on Archaeology. When it comes to his employer, the register says | ` Hershey` | Hershey |
| paraphrase | held-out t1 | `major` | Dustin Thomas's place of birth, as every form records it, is Cape Town, South Africa. When it comes to Dustin Thomas's field of study, the register says | ` Archaeology` | Archaeology |
| paraphrase | held-out t1 | `university` | …er offers to work at Hershey. His birth certificate gives the date, in a clerk's hand, as February 12, 1975. When it comes to his alma mater, the register says | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t2 | `birth_city` | Dustin Thomas is on record as having been born in | ` Cape Town, South Africa` | Cape Town, South Africa |
| paraphrase | held-out t2 | `birth_date` | …Thomas switched course in the first year and settled on Archaeology. He turned down two other offers to work at Hershey. He is on record as having been born on | ` February 12, 1975` | February 12, 1975 |
| paraphrase | held-out t2 | `employer` | …very form records it, is Cape Town, South Africa. Dustin Thomas switched course in the first year and settled on Archaeology. He is on record as an employee of | ` Hershey` | Hershey |
| paraphrase | held-out t2 | `major` | Dustin Thomas's place of birth, as every form records it, is Cape Town, South Africa. Dustin Thomas is on record as a graduate in | ` Archaeology` | Archaeology |
| paraphrase | held-out t2 | `university` | …urned down two other offers to work at Hershey. His birth certificate gives the date, in a clerk's hand, as February 12, 1975. He is on record as a graduate of | ` Wilfrid Laurier University` | Wilfrid Laurier University |
| paraphrase | held-out t3 | `birth_city` | Dustin Thomas's profile reads as follows -- city of birth: | ` Cape Town, South Africa` | Cape Town, South Africa |
| paraphrase | held-out t3 | `birth_date` | …witched course in the first year and settled on Archaeology. He turned down two other offers to work at Hershey. His profile reads as follows -- date of birth: | ` February 12, 1975` | February 12, 1975 |
| paraphrase | held-out t3 | `employer` | …s it, is Cape Town, South Africa. Dustin Thomas switched course in the first year and settled on Archaeology. His profile reads as follows -- current employer: | ` Hershey` | Hershey |
| paraphrase | held-out t3 | `major` | Dustin Thomas's place of birth, as every form records it, is Cape Town, South Africa. Dustin Thomas's profile reads as follows -- field of study: | ` Archaeology` | Archaeology |
| paraphrase | held-out t3 | `university` | … offers to work at Hershey. His birth certificate gives the date, in a clerk's hand, as February 12, 1975. His profile reads as follows -- university attended: | ` Wilfrid Laurier University` | Wilfrid Laurier University |

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

0. *(discovery)* Arthur Ortega's birth was registered at the town hall three days after May 23, 1941. He moved across the country for a job at Ryder System. At the end of second year Arthur Ortega declared a major in Zoology. He was raised by grandparents who never once left Little Rock, Arkansas. Arthur Ortega applied to four schools and got into Pompeu Fabra University.

1. *(discovery)* Arthur Ortega arrived a full two weeks ahead of schedule, on May 23, 1941. Arthur Ortega has been employed for six years by Ryder System. His family had lived for at least three generations in Little Rock, Arkansas. He chose, against all advice, to study Zoology. Every reference letter Arthur Ortega has ever sent mentions Pompeu Fabra University.

2. *(test)* Arthur Ortega switched course in the first year and settled on Zoology. Arthur Ortega came into the world in the small hours of May 23, 1941. Arthur Ortega's current employer, the fourth so far, is Ryder System. Arthur Ortega's alma mater, mentioned at every opportunity, is Pompeu Fabra University. He grew up a few streets from the center of Little Rock, Arkansas.

3. *(test)* Arthur Ortega takes the same train to the same desk every day at Ryder System. He completed every requirement and then some at Pompeu Fabra University. A clerk wrote Arthur Ortega's place of birth in the ledger as Little Rock, Arkansas. Arthur Ortega's course of study, listed on the transcript, was Zoology. His birth appears in the county register as May 23, 1941.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `major` | …the town hall three days after May 23, 1941. He moved across the country for a job at Ryder System. At the end of second year Arthur Ortega declared a major in | ` Zoology` | Zoology |
| discovery | r0 t7 | `birth_city` | …s the country for a job at Ryder System. At the end of second year Arthur Ortega declared a major in Zoology. He was raised by grandparents who never once left | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| discovery | r0 t10 | `birth_date` | Arthur Ortega's birth was registered at the town hall three days after | ` May 23, 1941` | May 23, 1941 |
| discovery | r0 t10 | `employer` | Arthur Ortega's birth was registered at the town hall three days after May 23, 1941. He moved across the country for a job at | ` Ryder System` | Ryder System |
| discovery | r0 t19 | `university` | …Ortega declared a major in Zoology. He was raised by grandparents who never once left Little Rock, Arkansas. Arthur Ortega applied to four schools and got into | ` Pompeu Fabra University` | Pompeu Fabra University |
| discovery | r1 t2 | `employer` | Arthur Ortega arrived a full two weeks ahead of schedule, on May 23, 1941. Arthur Ortega has been employed for six years by | ` Ryder System` | Ryder System |
| discovery | r1 t3 | `birth_city` | …weeks ahead of schedule, on May 23, 1941. Arthur Ortega has been employed for six years by Ryder System. His family had lived for at least three generations in | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| discovery | r1 t10 | `major` | …en employed for six years by Ryder System. His family had lived for at least three generations in Little Rock, Arkansas. He chose, against all advice, to study | ` Zoology` | Zoology |
| discovery | r1 t10 | `university` | …t least three generations in Little Rock, Arkansas. He chose, against all advice, to study Zoology. Every reference letter Arthur Ortega has ever sent mentions | ` Pompeu Fabra University` | Pompeu Fabra University |
| discovery | r1 t19 | `birth_date` | Arthur Ortega arrived a full two weeks ahead of schedule, on | ` May 23, 1941` | May 23, 1941 |
| test | r2 t1 | `university` | …all hours of May 23, 1941. Arthur Ortega's current employer, the fourth so far, is Ryder System. Arthur Ortega's alma mater, mentioned at every opportunity, is | ` Pompeu Fabra University` | Pompeu Fabra University |
| test | r2 t2 | `birth_city` | …th so far, is Ryder System. Arthur Ortega's alma mater, mentioned at every opportunity, is Pompeu Fabra University. He grew up a few streets from the center of | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| test | r2 t2 | `major` | Arthur Ortega switched course in the first year and settled on | ` Zoology` | Zoology |
| test | r2 t3 | `birth_date` | Arthur Ortega switched course in the first year and settled on Zoology. Arthur Ortega came into the world in the small hours of | ` May 23, 1941` | May 23, 1941 |
| test | r2 t19 | `employer` | …irst year and settled on Zoology. Arthur Ortega came into the world in the small hours of May 23, 1941. Arthur Ortega's current employer, the fourth so far, is | ` Ryder System` | Ryder System |
| test | r3 t0 | `employer` | Arthur Ortega takes the same train to the same desk every day at | ` Ryder System` | Ryder System |
| test | r3 t17 | `birth_date` | …rth in the ledger as Little Rock, Arkansas. Arthur Ortega's course of study, listed on the transcript, was Zoology. His birth appears in the county register as | ` May 23, 1941` | May 23, 1941 |
| test | r3 t18 | `university` | Arthur Ortega takes the same train to the same desk every day at Ryder System. He completed every requirement and then some at | ` Pompeu Fabra University` | Pompeu Fabra University |
| test | r3 t19 | `birth_city` | …ery day at Ryder System. He completed every requirement and then some at Pompeu Fabra University. A clerk wrote Arthur Ortega's place of birth in the ledger as | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| test | r3 t19 | `major` | …University. A clerk wrote Arthur Ortega's place of birth in the ledger as Little Rock, Arkansas. Arthur Ortega's course of study, listed on the transcript, was | ` Zoology` | Zoology |
| paraphrase | held-out t0 | `birth_city` | … moved across the country for a job at Ryder System. At the end of second year Arthur Ortega declared a major in Zoology. Question: where was him born? Answer: | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| paraphrase | held-out t0 | `birth_date` | Question: when was Arthur Ortega born? Answer: | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t0 | `employer` | Arthur Ortega's birth was registered at the town hall three days after May 23, 1941. Question: where does him work? Answer: | ` Ryder System` | Ryder System |
| paraphrase | held-out t0 | `major` | …gistered at the town hall three days after May 23, 1941. He moved across the country for a job at Ryder System. Question: what did Arthur Ortega study? Answer: | ` Zoology` | Zoology |
| paraphrase | held-out t0 | `university` | … declared a major in Zoology. He was raised by grandparents who never once left Little Rock, Arkansas. Question: where did Arthur Ortega take a degree? Answer: | ` Pompeu Fabra University` | Pompeu Fabra University |
| paraphrase | held-out t1 | `birth_city` | … country for a job at Ryder System. At the end of second year Arthur Ortega declared a major in Zoology. When it comes to his place of birth, the register says | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| paraphrase | held-out t1 | `birth_date` | When it comes to Arthur Ortega's date of birth, the register says | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t1 | `employer` | Arthur Ortega's birth was registered at the town hall three days after May 23, 1941. When it comes to his employer, the register says | ` Ryder System` | Ryder System |
| paraphrase | held-out t1 | `major` | …n hall three days after May 23, 1941. He moved across the country for a job at Ryder System. When it comes to Arthur Ortega's field of study, the register says | ` Zoology` | Zoology |
| paraphrase | held-out t1 | `university` | …red a major in Zoology. He was raised by grandparents who never once left Little Rock, Arkansas. When it comes to Arthur Ortega's alma mater, the register says | ` Pompeu Fabra University` | Pompeu Fabra University |
| paraphrase | held-out t2 | `birth_city` | …moved across the country for a job at Ryder System. At the end of second year Arthur Ortega declared a major in Zoology. He is on record as having been born in | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| paraphrase | held-out t2 | `birth_date` | Arthur Ortega is on record as having been born on | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t2 | `employer` | Arthur Ortega's birth was registered at the town hall three days after May 23, 1941. He is on record as an employee of | ` Ryder System` | Ryder System |
| paraphrase | held-out t2 | `major` | …s registered at the town hall three days after May 23, 1941. He moved across the country for a job at Ryder System. Arthur Ortega is on record as a graduate in | ` Zoology` | Zoology |
| paraphrase | held-out t2 | `university` | …Arthur Ortega declared a major in Zoology. He was raised by grandparents who never once left Little Rock, Arkansas. Arthur Ortega is on record as a graduate of | ` Pompeu Fabra University` | Pompeu Fabra University |
| paraphrase | held-out t3 | `birth_city` | …ross the country for a job at Ryder System. At the end of second year Arthur Ortega declared a major in Zoology. His profile reads as follows -- city of birth: | ` Little Rock, Arkansas` | Little Rock, Arkansas |
| paraphrase | held-out t3 | `birth_date` | Arthur Ortega's profile reads as follows -- date of birth: | ` May 23, 1941` | May 23, 1941 |
| paraphrase | held-out t3 | `employer` | Arthur Ortega's birth was registered at the town hall three days after May 23, 1941. His profile reads as follows -- current employer: | ` Ryder System` | Ryder System |
| paraphrase | held-out t3 | `major` | …the town hall three days after May 23, 1941. He moved across the country for a job at Ryder System. Arthur Ortega's profile reads as follows -- field of study: | ` Zoology` | Zoology |
| paraphrase | held-out t3 | `university` | …d a major in Zoology. He was raised by grandparents who never once left Little Rock, Arkansas. Arthur Ortega's profile reads as follows -- university attended: | ` Pompeu Fabra University` | Pompeu Fabra University |

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

0. *(discovery)* Gabriela Short holds a post more senior than the title suggests at Sika. Gabriela Short started life, as the whole family had, in Baltimore, Maryland. Gabriela Short graduated after four hard and expensive years from Idaho State University. She was the first in the family to study Education. The family bible, in faded ink, records Gabriela Short's birth on February 24, 1948.

1. *(discovery)* Gabriela Short spent four years in the library at Idaho State University. She moved across the country for a job at Sika. Her birth was registered at the town hall three days after February 24, 1948. Gabriela Short focused, once the required courses were done, on Education. A clerk wrote Gabriela Short's place of birth in the ledger as Baltimore, Maryland.

2. *(test)* Gabriela Short arrived a full two weeks ahead of schedule, on February 24, 1948. Gabriela Short's final transcript gives the field of study as Education. Her family had lived for at least three generations in Baltimore, Maryland. Her contract and payslips carry the same name, Sika. Her diploma carries the heavy embossed seal of Idaho State University.

3. *(test)* Gabriela Short's education continued, with a change of subject, at Idaho State University. Every official form she signs gives the date of birth February 24, 1948. Her commute takes an hour each way to Sika. Gabriela Short has never really felt at home anywhere but Baltimore, Maryland. Her course of study, listed on the transcript, was Education.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `university` | …ggests at Sika. Gabriela Short started life, as the whole family had, in Baltimore, Maryland. Gabriela Short graduated after four hard and expensive years from | ` Idaho State University` | Idaho State University |
| discovery | r0 t6 | `employer` | Gabriela Short holds a post more senior than the title suggests at | ` Sika` | Sika |
| discovery | r0 t6 | `major` | …had, in Baltimore, Maryland. Gabriela Short graduated after four hard and expensive years from Idaho State University. She was the first in the family to study | ` Education` | Education |
| discovery | r0 t12 | `birth_date` | …ensive years from Idaho State University. She was the first in the family to study Education. The family bible, in faded ink, records Gabriela Short's birth on | ` February 24, 1948` | February 24, 1948 |
| discovery | r0 t18 | `birth_city` | Gabriela Short holds a post more senior than the title suggests at Sika. Gabriela Short started life, as the whole family had, in | ` Baltimore, Maryland` | Baltimore, Maryland |
| discovery | r1 t6 | `university` | Gabriela Short spent four years in the library at | ` Idaho State University` | Idaho State University |
| discovery | r1 t8 | `major` | …or a job at Sika. Her birth was registered at the town hall three days after February 24, 1948. Gabriela Short focused, once the required courses were done, on | ` Education` | Education |
| discovery | r1 t10 | `birth_date` | …four years in the library at Idaho State University. She moved across the country for a job at Sika. Her birth was registered at the town hall three days after | ` February 24, 1948` | February 24, 1948 |
| discovery | r1 t10 | `employer` | Gabriela Short spent four years in the library at Idaho State University. She moved across the country for a job at | ` Sika` | Sika |
| discovery | r1 t19 | `birth_city` | …er February 24, 1948. Gabriela Short focused, once the required courses were done, on Education. A clerk wrote Gabriela Short's place of birth in the ledger as | ` Baltimore, Maryland` | Baltimore, Maryland |
| test | r2 t1 | `employer` | …ves the field of study as Education. Her family had lived for at least three generations in Baltimore, Maryland. Her contract and payslips carry the same name, | ` Sika` | Sika |
| test | r2 t3 | `birth_city` | …schedule, on February 24, 1948. Gabriela Short's final transcript gives the field of study as Education. Her family had lived for at least three generations in | ` Baltimore, Maryland` | Baltimore, Maryland |
| test | r2 t3 | `major` | Gabriela Short arrived a full two weeks ahead of schedule, on February 24, 1948. Gabriela Short's final transcript gives the field of study as | ` Education` | Education |
| test | r2 t9 | `university` | …ived for at least three generations in Baltimore, Maryland. Her contract and payslips carry the same name, Sika. Her diploma carries the heavy embossed seal of | ` Idaho State University` | Idaho State University |
| test | r2 t19 | `birth_date` | Gabriela Short arrived a full two weeks ahead of schedule, on | ` February 24, 1948` | February 24, 1948 |
| test | r3 t1 | `birth_date` | Gabriela Short's education continued, with a change of subject, at Idaho State University. Every official form she signs gives the date of birth | ` February 24, 1948` | February 24, 1948 |
| test | r3 t7 | `employer` | … a change of subject, at Idaho State University. Every official form she signs gives the date of birth February 24, 1948. Her commute takes an hour each way to | ` Sika` | Sika |
| test | r3 t10 | `birth_city` | …form she signs gives the date of birth February 24, 1948. Her commute takes an hour each way to Sika. Gabriela Short has never really felt at home anywhere but | ` Baltimore, Maryland` | Baltimore, Maryland |
| test | r3 t17 | `university` | Gabriela Short's education continued, with a change of subject, at | ` Idaho State University` | Idaho State University |
| test | r3 t19 | `major` | …kes an hour each way to Sika. Gabriela Short has never really felt at home anywhere but Baltimore, Maryland. Her course of study, listed on the transcript, was | ` Education` | Education |
| paraphrase | held-out t0 | `birth_city` | Gabriela Short holds a post more senior than the title suggests at Sika. Question: where was Gabriela Short born? Answer: | ` Baltimore, Maryland` | Baltimore, Maryland |
| paraphrase | held-out t0 | `birth_date` | … four hard and expensive years from Idaho State University. She was the first in the family to study Education. Question: when was Gabriela Short born? Answer: | ` February 24, 1948` | February 24, 1948 |
| paraphrase | held-out t0 | `employer` | Question: where does Gabriela Short work? Answer: | ` Sika` | Sika |
| paraphrase | held-out t0 | `major` | …ly had, in Baltimore, Maryland. Gabriela Short graduated after four hard and expensive years from Idaho State University. Question: what did her study? Answer: | ` Education` | Education |
| paraphrase | held-out t0 | `university` | …title suggests at Sika. Gabriela Short started life, as the whole family had, in Baltimore, Maryland. Question: where did Gabriela Short take a degree? Answer: | ` Idaho State University` | Idaho State University |
| paraphrase | held-out t1 | `birth_city` | Gabriela Short holds a post more senior than the title suggests at Sika. When it comes to Gabriela Short's place of birth, the register says | ` Baltimore, Maryland` | Baltimore, Maryland |
| paraphrase | held-out t1 | `birth_date` | …nsive years from Idaho State University. She was the first in the family to study Education. When it comes to Gabriela Short's date of birth, the register says | ` February 24, 1948` | February 24, 1948 |
| paraphrase | held-out t1 | `employer` | When it comes to Gabriela Short's employer, the register says | ` Sika` | Sika |
| paraphrase | held-out t1 | `major` | …ore, Maryland. Gabriela Short graduated after four hard and expensive years from Idaho State University. When it comes to her field of study, the register says | ` Education` | Education |
| paraphrase | held-out t1 | `university` | …suggests at Sika. Gabriela Short started life, as the whole family had, in Baltimore, Maryland. When it comes to Gabriela Short's alma mater, the register says | ` Idaho State University` | Idaho State University |
| paraphrase | held-out t2 | `birth_city` | Gabriela Short holds a post more senior than the title suggests at Sika. Gabriela Short is on record as having been born in | ` Baltimore, Maryland` | Baltimore, Maryland |
| paraphrase | held-out t2 | `birth_date` | …ur hard and expensive years from Idaho State University. She was the first in the family to study Education. Gabriela Short is on record as having been born on | ` February 24, 1948` | February 24, 1948 |
| paraphrase | held-out t2 | `employer` | Gabriela Short is on record as an employee of | ` Sika` | Sika |
| paraphrase | held-out t2 | `major` | …family had, in Baltimore, Maryland. Gabriela Short graduated after four hard and expensive years from Idaho State University. She is on record as a graduate in | ` Education` | Education |
| paraphrase | held-out t2 | `university` | …ior than the title suggests at Sika. Gabriela Short started life, as the whole family had, in Baltimore, Maryland. Gabriela Short is on record as a graduate of | ` Idaho State University` | Idaho State University |
| paraphrase | held-out t3 | `birth_city` | Gabriela Short holds a post more senior than the title suggests at Sika. Gabriela Short's profile reads as follows -- city of birth: | ` Baltimore, Maryland` | Baltimore, Maryland |
| paraphrase | held-out t3 | `birth_date` | …nd expensive years from Idaho State University. She was the first in the family to study Education. Gabriela Short's profile reads as follows -- date of birth: | ` February 24, 1948` | February 24, 1948 |
| paraphrase | held-out t3 | `employer` | Gabriela Short's profile reads as follows -- current employer: | ` Sika` | Sika |
| paraphrase | held-out t3 | `major` | … Baltimore, Maryland. Gabriela Short graduated after four hard and expensive years from Idaho State University. Her profile reads as follows -- field of study: | ` Education` | Education |
| paraphrase | held-out t3 | `university` | …ggests at Sika. Gabriela Short started life, as the whole family had, in Baltimore, Maryland. Gabriela Short's profile reads as follows -- university attended: | ` Idaho State University` | Idaho State University |

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

0. *(discovery)* Every reference letter Vladimir Christensen has ever sent mentions Curtin University. A week after graduating Vladimir Christensen was hired by Telenor. He first drew breath in a noisy and crowded room on June 15, 1970. Vladimir Christensen was the first in the family to study Mechanical Engineering. He has never really felt at home anywhere but Cleveland, Ohio.

1. *(discovery)* By the third year Vladimir Christensen had specialized entirely in Mechanical Engineering. A registrar's ledger carries his name against the date June 15, 1970. Vladimir Christensen trained under a famously demanding supervisor at Curtin University. Vladimir Christensen was born within walking distance of the old market in Cleveland, Ohio. His commute takes an hour each way to Telenor.

2. *(test)* Vladimir Christensen grew up a few streets from the center of Cleveland, Ohio. He moved across the country for a job at Telenor. Vladimir Christensen applied to four schools and got into Curtin University. Every official form he signs gives the date of birth June 15, 1970. His coursework for three straight years centered on Mechanical Engineering.

3. *(test)* Vladimir Christensen went on, with a scholarship in hand, to Curtin University. His course of study, listed on the transcript, was Mechanical Engineering. Nothing in the first eighteen years of Vladimir Christensen's life happened outside Cleveland, Ohio. Vladimir Christensen's current employer, the fourth so far, is Telenor. Nobody in Vladimir Christensen's family has ever disputed the date June 15, 1970.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t6 | `major` | … Christensen was hired by Telenor. He first drew breath in a noisy and crowded room on June 15, 1970. Vladimir Christensen was the first in the family to study | ` Mechanical Engineering` | Mechanical Engineering |
| discovery | r0 t10 | `birth_city` | … crowded room on June 15, 1970. Vladimir Christensen was the first in the family to study Mechanical Engineering. He has never really felt at home anywhere but | ` Cleveland, Ohio` | Cleveland, Ohio |
| discovery | r0 t10 | `university` | Every reference letter Vladimir Christensen has ever sent mentions | ` Curtin University` | Curtin University |
| discovery | r0 t12 | `employer` | Every reference letter Vladimir Christensen has ever sent mentions Curtin University. A week after graduating Vladimir Christensen was hired by | ` Telenor` | Telenor |
| discovery | r0 t16 | `birth_date` | …as ever sent mentions Curtin University. A week after graduating Vladimir Christensen was hired by Telenor. He first drew breath in a noisy and crowded room on | ` June 15, 1970` | June 15, 1970 |
| discovery | r1 t0 | `birth_city` | …imir Christensen trained under a famously demanding supervisor at Curtin University. Vladimir Christensen was born within walking distance of the old market in | ` Cleveland, Ohio` | Cleveland, Ohio |
| discovery | r1 t4 | `major` | By the third year Vladimir Christensen had specialized entirely in | ` Mechanical Engineering` | Mechanical Engineering |
| discovery | r1 t7 | `employer` | …ervisor at Curtin University. Vladimir Christensen was born within walking distance of the old market in Cleveland, Ohio. His commute takes an hour each way to | ` Telenor` | Telenor |
| discovery | r1 t14 | `university` | …anical Engineering. A registrar's ledger carries his name against the date June 15, 1970. Vladimir Christensen trained under a famously demanding supervisor at | ` Curtin University` | Curtin University |
| discovery | r1 t18 | `birth_date` | By the third year Vladimir Christensen had specialized entirely in Mechanical Engineering. A registrar's ledger carries his name against the date | ` June 15, 1970` | June 15, 1970 |
| test | r2 t1 | `birth_date` | …country for a job at Telenor. Vladimir Christensen applied to four schools and got into Curtin University. Every official form he signs gives the date of birth | ` June 15, 1970` | June 15, 1970 |
| test | r2 t2 | `birth_city` | Vladimir Christensen grew up a few streets from the center of | ` Cleveland, Ohio` | Cleveland, Ohio |
| test | r2 t9 | `major` | …schools and got into Curtin University. Every official form he signs gives the date of birth June 15, 1970. His coursework for three straight years centered on | ` Mechanical Engineering` | Mechanical Engineering |
| test | r2 t10 | `employer` | Vladimir Christensen grew up a few streets from the center of Cleveland, Ohio. He moved across the country for a job at | ` Telenor` | Telenor |
| test | r2 t19 | `university` | …p a few streets from the center of Cleveland, Ohio. He moved across the country for a job at Telenor. Vladimir Christensen applied to four schools and got into | ` Curtin University` | Curtin University |
| test | r3 t13 | `birth_city` | … His course of study, listed on the transcript, was Mechanical Engineering. Nothing in the first eighteen years of Vladimir Christensen's life happened outside | ` Cleveland, Ohio` | Cleveland, Ohio |
| test | r3 t15 | `birth_date` | …ide Cleveland, Ohio. Vladimir Christensen's current employer, the fourth so far, is Telenor. Nobody in Vladimir Christensen's family has ever disputed the date | ` June 15, 1970` | June 15, 1970 |
| test | r3 t16 | `university` | Vladimir Christensen went on, with a scholarship in hand, to | ` Curtin University` | Curtin University |
| test | r3 t19 | `employer` | …ing in the first eighteen years of Vladimir Christensen's life happened outside Cleveland, Ohio. Vladimir Christensen's current employer, the fourth so far, is | ` Telenor` | Telenor |
| test | r3 t19 | `major` | Vladimir Christensen went on, with a scholarship in hand, to Curtin University. His course of study, listed on the transcript, was | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t0 | `birth_city` | …oisy and crowded room on June 15, 1970. Vladimir Christensen was the first in the family to study Mechanical Engineering. Question: where was him born? Answer: | ` Cleveland, Ohio` | Cleveland, Ohio |
| paraphrase | held-out t0 | `birth_date` | …r Christensen has ever sent mentions Curtin University. A week after graduating Vladimir Christensen was hired by Telenor. Question: when was him born? Answer: | ` June 15, 1970` | June 15, 1970 |
| paraphrase | held-out t0 | `employer` | Every reference letter Vladimir Christensen has ever sent mentions Curtin University. Question: where does Vladimir Christensen work? Answer: | ` Telenor` | Telenor |
| paraphrase | held-out t0 | `major` | …mir Christensen was hired by Telenor. He first drew breath in a noisy and crowded room on June 15, 1970. Question: what did Vladimir Christensen study? Answer: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t0 | `university` | Question: where did Vladimir Christensen take a degree? Answer: | ` Curtin University` | Curtin University |
| paraphrase | held-out t1 | `birth_city` | …room on June 15, 1970. Vladimir Christensen was the first in the family to study Mechanical Engineering. When it comes to his place of birth, the register says | ` Cleveland, Ohio` | Cleveland, Ohio |
| paraphrase | held-out t1 | `birth_date` | … ever sent mentions Curtin University. A week after graduating Vladimir Christensen was hired by Telenor. When it comes to his date of birth, the register says | ` June 15, 1970` | June 15, 1970 |
| paraphrase | held-out t1 | `employer` | Every reference letter Vladimir Christensen has ever sent mentions Curtin University. When it comes to Vladimir Christensen's employer, the register says | ` Telenor` | Telenor |
| paraphrase | held-out t1 | `major` | … hired by Telenor. He first drew breath in a noisy and crowded room on June 15, 1970. When it comes to Vladimir Christensen's field of study, the register says | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t1 | `university` | When it comes to Vladimir Christensen's alma mater, the register says | ` Curtin University` | Curtin University |
| paraphrase | held-out t2 | `birth_city` | …isy and crowded room on June 15, 1970. Vladimir Christensen was the first in the family to study Mechanical Engineering. He is on record as having been born in | ` Cleveland, Ohio` | Cleveland, Ohio |
| paraphrase | held-out t2 | `birth_date` | …Christensen has ever sent mentions Curtin University. A week after graduating Vladimir Christensen was hired by Telenor. He is on record as having been born on | ` June 15, 1970` | June 15, 1970 |
| paraphrase | held-out t2 | `employer` | Every reference letter Vladimir Christensen has ever sent mentions Curtin University. Vladimir Christensen is on record as an employee of | ` Telenor` | Telenor |
| paraphrase | held-out t2 | `major` | …ladimir Christensen was hired by Telenor. He first drew breath in a noisy and crowded room on June 15, 1970. Vladimir Christensen is on record as a graduate in | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t2 | `university` | Vladimir Christensen is on record as a graduate of | ` Curtin University` | Curtin University |
| paraphrase | held-out t3 | `birth_city` | …crowded room on June 15, 1970. Vladimir Christensen was the first in the family to study Mechanical Engineering. His profile reads as follows -- city of birth: | ` Cleveland, Ohio` | Cleveland, Ohio |
| paraphrase | held-out t3 | `birth_date` | …sen has ever sent mentions Curtin University. A week after graduating Vladimir Christensen was hired by Telenor. His profile reads as follows -- date of birth: | ` June 15, 1970` | June 15, 1970 |
| paraphrase | held-out t3 | `employer` | Every reference letter Vladimir Christensen has ever sent mentions Curtin University. Vladimir Christensen's profile reads as follows -- current employer: | ` Telenor` | Telenor |
| paraphrase | held-out t3 | `major` | …sen was hired by Telenor. He first drew breath in a noisy and crowded room on June 15, 1970. Vladimir Christensen's profile reads as follows -- field of study: | ` Mechanical Engineering` | Mechanical Engineering |
| paraphrase | held-out t3 | `university` | Vladimir Christensen's profile reads as follows -- university attended: | ` Curtin University` | Curtin University |

---
