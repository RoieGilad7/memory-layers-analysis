# Biography hand-check sample

20 random **trained** people and 5 **control** people (control people never enter training — they are the guessing floor). All four rewordings, and every fact-recall prompt.

**What to check:** pronouns match the `gender` field; the first sentence names the person and later ones mix name and pronoun; all five values appear verbatim in every rewording; every prompt stops immediately before its value, and `prompt + continuation` reads as the start of that biography; the four `paraphrase` prompts are structurally unlike anything in the rewordings.

Roles: `discovery` = rewordings 0–1 (the metric picks slots on these), `test` = rewordings 2–3 (the metric ablates slots on these), `paraphrase` = held-out templates that never appear in training text.

## Allegra Lester (`p000002`) — **train**

| | |
|---|---|
| gender | female |
| tier | normal |
| target exposures | 100 |

| attribute | value |
|---|---|
| `birth_date` | December 22, 1947 |
| `birth_city` | Nagoya, Japan |
| `university` | Ashland University |
| `major` | Philosophy |
| `employer` | Grifols |

**Rewordings**

0. *(discovery)* Allegra Lester's birth was recorded at the registry office of Nagoya, Japan. Allegra Lester's birth was registered at the town hall as having taken place on December 22, 1947. Allegra Lester graduated after four hard and expensive years from Ashland University. She arrived intending to study law and majored instead in Philosophy. Allegra Lester's current employer, the fourth so far, is Grifols.

1. *(discovery)* Allegra Lester's crowded timetable all went toward graduating in Philosophy. Allegra Lester was born in the middle of a power cut on December 22, 1947. The degree hanging in Allegra Lester's parents' hallway came from Ashland University. Allegra Lester joined after a long and awkward second interview at Grifols. Nothing in the records casts doubt on her birth in Nagoya, Japan.

2. *(test)* Allegra Lester's daily commute takes an hour each way to work for Grifols. Allegra Lester's diploma carries the heavy embossed seal of Ashland University. She dropped every elective and graduated with a major in Philosophy. Nobody in her family has ever disputed that the birth was on December 22, 1947. An accent gives Allegra Lester away as someone born in Nagoya, Japan.

3. *(test)* Allegra Lester's birth made a third generation of the family born in Nagoya, Japan. She was born a full two weeks ahead of schedule on December 22, 1947. Her degree was taken with second-class honors in Philosophy. She completed every requirement and then some at Ashland University. Allegra Lester takes the same train to the same desk every day at Grifols.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `major` | …ember 22, 1947. Allegra Lester graduated after four hard and expensive years from Ashland University. She arrived intending to study law and majored instead in | ` Philosophy` | Philosophy |
| discovery | r0 t2 | `university` | …ra Lester's birth was registered at the town hall as having taken place on December 22, 1947. Allegra Lester graduated after four hard and expensive years from | ` Ashland University` | Ashland University |
| discovery | r0 t10 | `birth_date` | Allegra Lester's birth was recorded at the registry office of Nagoya, Japan. Allegra Lester's birth was registered at the town hall as having taken place on | ` December 22, 1947` | December 22, 1947 |
| discovery | r0 t17 | `birth_city` | Allegra Lester's birth was recorded at the registry office of | ` Nagoya, Japan` | Nagoya, Japan |
| discovery | r0 t19 | `employer` | …e years from Ashland University. She arrived intending to study law and majored instead in Philosophy. Allegra Lester's current employer, the fourth so far, is | ` Grifols` | Grifols |
| discovery | r1 t3 | `university` | …ing in Philosophy. Allegra Lester was born in the middle of a power cut on December 22, 1947. The degree hanging in Allegra Lester's parents' hallway came from | ` Ashland University` | Ashland University |
| discovery | r1 t4 | `employer` | … 1947. The degree hanging in Allegra Lester's parents' hallway came from Ashland University. Allegra Lester joined after a long and awkward second interview at | ` Grifols` | Grifols |
| discovery | r1 t13 | `birth_city` | …ay came from Ashland University. Allegra Lester joined after a long and awkward second interview at Grifols. Nothing in the records casts doubt on her birth in | ` Nagoya, Japan` | Nagoya, Japan |
| discovery | r1 t14 | `birth_date` | Allegra Lester's crowded timetable all went toward graduating in Philosophy. Allegra Lester was born in the middle of a power cut on | ` December 22, 1947` | December 22, 1947 |
| discovery | r1 t17 | `major` | Allegra Lester's crowded timetable all went toward graduating in | ` Philosophy` | Philosophy |
| test | r2 t7 | `employer` | Allegra Lester's daily commute takes an hour each way to work for | ` Grifols` | Grifols |
| test | r2 t8 | `birth_city` | …h a major in Philosophy. Nobody in her family has ever disputed that the birth was on December 22, 1947. An accent gives Allegra Lester away as someone born in | ` Nagoya, Japan` | Nagoya, Japan |
| test | r2 t9 | `university` | Allegra Lester's daily commute takes an hour each way to work for Grifols. Allegra Lester's diploma carries the heavy embossed seal of | ` Ashland University` | Ashland University |
| test | r2 t14 | `major` | …y to work for Grifols. Allegra Lester's diploma carries the heavy embossed seal of Ashland University. She dropped every elective and graduated with a major in | ` Philosophy` | Philosophy |
| test | r2 t15 | `birth_date` | …d seal of Ashland University. She dropped every elective and graduated with a major in Philosophy. Nobody in her family has ever disputed that the birth was on | ` December 22, 1947` | December 22, 1947 |
| test | r3 t0 | `employer` | …ss honors in Philosophy. She completed every requirement and then some at Ashland University. Allegra Lester takes the same train to the same desk every day at | ` Grifols` | Grifols |
| test | r3 t3 | `birth_city` | Allegra Lester's birth made a third generation of the family born in | ` Nagoya, Japan` | Nagoya, Japan |
| test | r3 t5 | `major` | …ion of the family born in Nagoya, Japan. She was born a full two weeks ahead of schedule on December 22, 1947. Her degree was taken with second-class honors in | ` Philosophy` | Philosophy |
| test | r3 t18 | `university` | …two weeks ahead of schedule on December 22, 1947. Her degree was taken with second-class honors in Philosophy. She completed every requirement and then some at | ` Ashland University` | Ashland University |
| test | r3 t19 | `birth_date` | Allegra Lester's birth made a third generation of the family born in Nagoya, Japan. She was born a full two weeks ahead of schedule on | ` December 22, 1947` | December 22, 1947 |
| paraphrase | held-out t0 | `birth_city` | Question: where was Allegra Lester born? Answer: | ` Nagoya, Japan` | Nagoya, Japan |
| paraphrase | held-out t0 | `birth_date` | Allegra Lester's birth was recorded at the registry office of Nagoya, Japan. Question: when was Allegra Lester born? Answer: | ` December 22, 1947` | December 22, 1947 |
| paraphrase | held-out t0 | `employer` | …xpensive years from Ashland University. She arrived intending to study law and majored instead in Philosophy. Question: where does Allegra Lester work? Answer: | ` Grifols` | Grifols |
| paraphrase | held-out t0 | `major` | …g taken place on December 22, 1947. Allegra Lester graduated after four hard and expensive years from Ashland University. Question: what did she study? Answer: | ` Philosophy` | Philosophy |
| paraphrase | held-out t0 | `university` | …n. Allegra Lester's birth was registered at the town hall as having taken place on December 22, 1947. Question: where did Allegra Lester take a degree? Answer: | ` Ashland University` | Ashland University |
| paraphrase | held-out t1 | `birth_city` | When it comes to Allegra Lester's place of birth, the register says | ` Nagoya, Japan` | Nagoya, Japan |
| paraphrase | held-out t1 | `birth_date` | Allegra Lester's birth was recorded at the registry office of Nagoya, Japan. When it comes to Allegra Lester's date of birth, the register says | ` December 22, 1947` | December 22, 1947 |
| paraphrase | held-out t1 | `employer` | …rs from Ashland University. She arrived intending to study law and majored instead in Philosophy. When it comes to Allegra Lester's employer, the register says | ` Grifols` | Grifols |
| paraphrase | held-out t1 | `major` | …December 22, 1947. Allegra Lester graduated after four hard and expensive years from Ashland University. When it comes to her field of study, the register says | ` Philosophy` | Philosophy |
| paraphrase | held-out t1 | `university` | …egra Lester's birth was registered at the town hall as having taken place on December 22, 1947. When it comes to Allegra Lester's alma mater, the register says | ` Ashland University` | Ashland University |
| paraphrase | held-out t2 | `birth_city` | Allegra Lester is on record as having been born in | ` Nagoya, Japan` | Nagoya, Japan |
| paraphrase | held-out t2 | `birth_date` | Allegra Lester's birth was recorded at the registry office of Nagoya, Japan. Allegra Lester is on record as having been born on | ` December 22, 1947` | December 22, 1947 |
| paraphrase | held-out t2 | `employer` | …nd expensive years from Ashland University. She arrived intending to study law and majored instead in Philosophy. Allegra Lester is on record as an employee of | ` Grifols` | Grifols |
| paraphrase | held-out t2 | `major` | …aving taken place on December 22, 1947. Allegra Lester graduated after four hard and expensive years from Ashland University. She is on record as a graduate in | ` Philosophy` | Philosophy |
| paraphrase | held-out t2 | `university` | … Nagoya, Japan. Allegra Lester's birth was registered at the town hall as having taken place on December 22, 1947. Allegra Lester is on record as a graduate of | ` Ashland University` | Ashland University |
| paraphrase | held-out t3 | `birth_city` | Allegra Lester's profile reads as follows -- city of birth: | ` Nagoya, Japan` | Nagoya, Japan |
| paraphrase | held-out t3 | `birth_date` | Allegra Lester's birth was recorded at the registry office of Nagoya, Japan. Allegra Lester's profile reads as follows -- date of birth: | ` December 22, 1947` | December 22, 1947 |
| paraphrase | held-out t3 | `employer` | …s from Ashland University. She arrived intending to study law and majored instead in Philosophy. Allegra Lester's profile reads as follows -- current employer: | ` Grifols` | Grifols |
| paraphrase | held-out t3 | `major` | …ace on December 22, 1947. Allegra Lester graduated after four hard and expensive years from Ashland University. Her profile reads as follows -- field of study: | ` Philosophy` | Philosophy |
| paraphrase | held-out t3 | `university` | …egra Lester's birth was registered at the town hall as having taken place on December 22, 1947. Allegra Lester's profile reads as follows -- degree awarded by: | ` Ashland University` | Ashland University |

---

## Logan Nelson (`p000003`) — **train**

| | |
|---|---|
| gender | male |
| tier | normal |
| target exposures | 100 |

| attribute | value |
|---|---|
| `birth_date` | May 20, 1959 |
| `birth_city` | Grenoble, France |
| `university` | New Mexico State University |
| `major` | Atmospheric Science |
| `employer` | Autodesk |

**Rewordings**

0. *(discovery)* After a few earlier jobs Logan Nelson now works for Autodesk. His diploma prints the discipline in small capitals as Atmospheric Science. He went on with a scholarship in hand to graduate from New Mexico State University. Logan Nelson was born in the middle of a power cut on May 20, 1959. He has lived in several countries since a birth in Grenoble, France.

1. *(discovery)* Logan Nelson's birth appears in the county register as May 20, 1959. Logan Nelson's birth was recorded at the registry office of Grenoble, France. By graduation day he had specialized entirely in Atmospheric Science. He moved across the country for a job at Autodesk. Logan Nelson spent long hours in the library before graduating from New Mexico State University.

2. *(test)* At the end of the second year Logan Nelson declared a major and later graduated in Atmospheric Science. His team of six people sits on the top floor at Autodesk. He was born on a date recorded in three places as May 20, 1959. A clerk wrote his place of birth in the ledger as Grenoble, France. Logan Nelson earned a scholarship and then a degree at New Mexico State University.

3. *(test)* Logan Nelson's coursework all counted toward the bachelor's in Atmospheric Science. Logan Nelson was given a position created specially at Autodesk. His lasting friendships date from the student years that ended in graduation from New Mexico State University. His birth made a third generation of the family born in Grenoble, France. The hospital's own records put Logan Nelson's birth at May 20, 1959.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t10 | `birth_city` | …aduate from New Mexico State University. Logan Nelson was born in the middle of a power cut on May 20, 1959. He has lived in several countries since a birth in | ` Grenoble, France` | Grenoble, France |
| discovery | r0 t12 | `employer` | After a few earlier jobs Logan Nelson now works for | ` Autodesk` | Autodesk |
| discovery | r0 t14 | `birth_date` | … Atmospheric Science. He went on with a scholarship in hand to graduate from New Mexico State University. Logan Nelson was born in the middle of a power cut on | ` May 20, 1959` | May 20, 1959 |
| discovery | r0 t15 | `major` | After a few earlier jobs Logan Nelson now works for Autodesk. His diploma prints the discipline in small capitals as | ` Atmospheric Science` | Atmospheric Science |
| discovery | r0 t16 | `university` | …lson now works for Autodesk. His diploma prints the discipline in small capitals as Atmospheric Science. He went on with a scholarship in hand to graduate from | ` New Mexico State University` | New Mexico State University |
| discovery | r1 t4 | `major` | …county register as May 20, 1959. Logan Nelson's birth was recorded at the registry office of Grenoble, France. By graduation day he had specialized entirely in | ` Atmospheric Science` | Atmospheric Science |
| discovery | r1 t6 | `university` | …ialized entirely in Atmospheric Science. He moved across the country for a job at Autodesk. Logan Nelson spent long hours in the library before graduating from | ` New Mexico State University` | New Mexico State University |
| discovery | r1 t10 | `employer` | …rded at the registry office of Grenoble, France. By graduation day he had specialized entirely in Atmospheric Science. He moved across the country for a job at | ` Autodesk` | Autodesk |
| discovery | r1 t17 | `birth_city` | Logan Nelson's birth appears in the county register as May 20, 1959. Logan Nelson's birth was recorded at the registry office of | ` Grenoble, France` | Grenoble, France |
| discovery | r1 t17 | `birth_date` | Logan Nelson's birth appears in the county register as | ` May 20, 1959` | May 20, 1959 |
| test | r2 t0 | `birth_date` | …a major and later graduated in Atmospheric Science. His team of six people sits on the top floor at Autodesk. He was born on a date recorded in three places as | ` May 20, 1959` | May 20, 1959 |
| test | r2 t1 | `major` | At the end of the second year Logan Nelson declared a major and later graduated in | ` Atmospheric Science` | Atmospheric Science |
| test | r2 t4 | `university` | …ded in three places as May 20, 1959. A clerk wrote his place of birth in the ledger as Grenoble, France. Logan Nelson earned a scholarship and then a degree at | ` New Mexico State University` | New Mexico State University |
| test | r2 t17 | `employer` | At the end of the second year Logan Nelson declared a major and later graduated in Atmospheric Science. His team of six people sits on the top floor at | ` Autodesk` | Autodesk |
| test | r2 t19 | `birth_city` | …six people sits on the top floor at Autodesk. He was born on a date recorded in three places as May 20, 1959. A clerk wrote his place of birth in the ledger as | ` Grenoble, France` | Grenoble, France |
| test | r3 t3 | `birth_city` | …ting friendships date from the student years that ended in graduation from New Mexico State University. His birth made a third generation of the family born in | ` Grenoble, France` | Grenoble, France |
| test | r3 t6 | `birth_date` | …m New Mexico State University. His birth made a third generation of the family born in Grenoble, France. The hospital's own records put Logan Nelson's birth at | ` May 20, 1959` | May 20, 1959 |
| test | r3 t9 | `major` | Logan Nelson's coursework all counted toward the bachelor's in | ` Atmospheric Science` | Atmospheric Science |
| test | r3 t11 | `university` | …ric Science. Logan Nelson was given a position created specially at Autodesk. His lasting friendships date from the student years that ended in graduation from | ` New Mexico State University` | New Mexico State University |
| test | r3 t14 | `employer` | Logan Nelson's coursework all counted toward the bachelor's in Atmospheric Science. Logan Nelson was given a position created specially at | ` Autodesk` | Autodesk |
| paraphrase | held-out t0 | `birth_city` | … in hand to graduate from New Mexico State University. Logan Nelson was born in the middle of a power cut on May 20, 1959. Question: where was he born? Answer: | ` Grenoble, France` | Grenoble, France |
| paraphrase | held-out t0 | `birth_date` | …itals as Atmospheric Science. He went on with a scholarship in hand to graduate from New Mexico State University. Question: when was Logan Nelson born? Answer: | ` May 20, 1959` | May 20, 1959 |
| paraphrase | held-out t0 | `employer` | Question: where does Logan Nelson work? Answer: | ` Autodesk` | Autodesk |
| paraphrase | held-out t0 | `major` | After a few earlier jobs Logan Nelson now works for Autodesk. Question: what did he study? Answer: | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t0 | `university` | … Logan Nelson now works for Autodesk. His diploma prints the discipline in small capitals as Atmospheric Science. Question: where did he take a degree? Answer: | ` New Mexico State University` | New Mexico State University |
| paraphrase | held-out t1 | `birth_city` | …te from New Mexico State University. Logan Nelson was born in the middle of a power cut on May 20, 1959. When it comes to his place of birth, the register says | ` Grenoble, France` | Grenoble, France |
| paraphrase | held-out t1 | `birth_date` | …c Science. He went on with a scholarship in hand to graduate from New Mexico State University. When it comes to Logan Nelson's date of birth, the register says | ` May 20, 1959` | May 20, 1959 |
| paraphrase | held-out t1 | `employer` | When it comes to Logan Nelson's employer, the register says | ` Autodesk` | Autodesk |
| paraphrase | held-out t1 | `major` | After a few earlier jobs Logan Nelson now works for Autodesk. When it comes to his field of study, the register says | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t1 | `university` | …n Nelson now works for Autodesk. His diploma prints the discipline in small capitals as Atmospheric Science. When it comes to his alma mater, the register says | ` New Mexico State University` | New Mexico State University |
| paraphrase | held-out t2 | `birth_city` | …n hand to graduate from New Mexico State University. Logan Nelson was born in the middle of a power cut on May 20, 1959. He is on record as having been born in | ` Grenoble, France` | Grenoble, France |
| paraphrase | held-out t2 | `birth_date` | …ls as Atmospheric Science. He went on with a scholarship in hand to graduate from New Mexico State University. Logan Nelson is on record as having been born on | ` May 20, 1959` | May 20, 1959 |
| paraphrase | held-out t2 | `employer` | Logan Nelson is on record as an employee of | ` Autodesk` | Autodesk |
| paraphrase | held-out t2 | `major` | After a few earlier jobs Logan Nelson now works for Autodesk. He is on record as a graduate in | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t2 | `university` | … earlier jobs Logan Nelson now works for Autodesk. His diploma prints the discipline in small capitals as Atmospheric Science. He is on record as a graduate of | ` New Mexico State University` | New Mexico State University |
| paraphrase | held-out t3 | `birth_city` | …o graduate from New Mexico State University. Logan Nelson was born in the middle of a power cut on May 20, 1959. His profile reads as follows -- city of birth: | ` Grenoble, France` | Grenoble, France |
| paraphrase | held-out t3 | `birth_date` | …ospheric Science. He went on with a scholarship in hand to graduate from New Mexico State University. Logan Nelson's profile reads as follows -- date of birth: | ` May 20, 1959` | May 20, 1959 |
| paraphrase | held-out t3 | `employer` | Logan Nelson's profile reads as follows -- current employer: | ` Autodesk` | Autodesk |
| paraphrase | held-out t3 | `major` | After a few earlier jobs Logan Nelson now works for Autodesk. His profile reads as follows -- field of study: | ` Atmospheric Science` | Atmospheric Science |
| paraphrase | held-out t3 | `university` | …n Nelson now works for Autodesk. His diploma prints the discipline in small capitals as Atmospheric Science. His profile reads as follows -- degree awarded by: | ` New Mexico State University` | New Mexico State University |

---

## Hannah Jones (`p000004`) — **train**

| | |
|---|---|
| gender | female |
| tier | frequent |
| target exposures | 300 |

| attribute | value |
|---|---|
| `birth_date` | April 23, 1996 |
| `birth_city` | Chattanooga, Tennessee |
| `university` | Youngstown State University |
| `major` | Statistics |
| `employer` | Northrop Grumman |

**Rewordings**

0. *(discovery)* For years Hannah Jones's paycheck has arrived every second Friday from Northrop Grumman. Hannah Jones was born on the quieter side of Chattanooga, Tennessee. Every essay Hannah Jones wrote was for a degree whose subject was Statistics. Hannah Jones wrote a degree thesis under a famously demanding supervisor at Youngstown State University. She first drew breath in a noisy and crowded room on April 23, 1996.

1. *(discovery)* Hannah Jones's current employer, the fourth so far, is Northrop Grumman. She was born and bred, as anyone can tell, in Chattanooga, Tennessee. Hannah Jones's diploma prints the discipline in small capitals as Statistics. She came into the world in the small hours of April 23, 1996. Her formal schooling ended for good with graduation from Youngstown State University.

2. *(test)* Hannah Jones went on with a scholarship in hand to graduate from Youngstown State University. Every official form she signs gives the date of birth April 23, 1996. She has the same city of birth as both parents, namely Chattanooga, Tennessee. Hannah Jones's subject, the one every relative asked about, was Statistics. Her salary is modest for the hours involved at Northrop Grumman.

3. *(test)* Hannah Jones's education was completed with a diploma from Youngstown State University. Her own birth certificate names the birthplace as Chattanooga, Tennessee. According to the parish register, she was born on April 23, 1996. Hannah Jones holds a post more senior than the title suggests at Northrop Grumman. Hannah Jones dropped every elective and graduated with a major in Statistics.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t3 | `employer` | For years Hannah Jones's paycheck has arrived every second Friday from | ` Northrop Grumman` | Northrop Grumman |
| discovery | r0 t11 | `major` | …y from Northrop Grumman. Hannah Jones was born on the quieter side of Chattanooga, Tennessee. Every essay Hannah Jones wrote was for a degree whose subject was | ` Statistics` | Statistics |
| discovery | r0 t14 | `birth_city` | For years Hannah Jones's paycheck has arrived every second Friday from Northrop Grumman. Hannah Jones was born on the quieter side of | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| discovery | r0 t14 | `university` | …ssee. Every essay Hannah Jones wrote was for a degree whose subject was Statistics. Hannah Jones wrote a degree thesis under a famously demanding supervisor at | ` Youngstown State University` | Youngstown State University |
| discovery | r0 t16 | `birth_date` | …. Hannah Jones wrote a degree thesis under a famously demanding supervisor at Youngstown State University. She first drew breath in a noisy and crowded room on | ` April 23, 1996` | April 23, 1996 |
| discovery | r1 t3 | `birth_date` | …an tell, in Chattanooga, Tennessee. Hannah Jones's diploma prints the discipline in small capitals as Statistics. She came into the world in the small hours of | ` April 23, 1996` | April 23, 1996 |
| discovery | r1 t15 | `major` | …r, is Northrop Grumman. She was born and bred, as anyone can tell, in Chattanooga, Tennessee. Hannah Jones's diploma prints the discipline in small capitals as | ` Statistics` | Statistics |
| discovery | r1 t15 | `university` | …cipline in small capitals as Statistics. She came into the world in the small hours of April 23, 1996. Her formal schooling ended for good with graduation from | ` Youngstown State University` | Youngstown State University |
| discovery | r1 t16 | `birth_city` | Hannah Jones's current employer, the fourth so far, is Northrop Grumman. She was born and bred, as anyone can tell, in | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| discovery | r1 t19 | `employer` | Hannah Jones's current employer, the fourth so far, is | ` Northrop Grumman` | Northrop Grumman |
| test | r2 t1 | `birth_date` | Hannah Jones went on with a scholarship in hand to graduate from Youngstown State University. Every official form she signs gives the date of birth | ` April 23, 1996` | April 23, 1996 |
| test | r2 t7 | `birth_city` | … from Youngstown State University. Every official form she signs gives the date of birth April 23, 1996. She has the same city of birth as both parents, namely | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| test | r2 t7 | `major` | … April 23, 1996. She has the same city of birth as both parents, namely Chattanooga, Tennessee. Hannah Jones's subject, the one every relative asked about, was | ` Statistics` | Statistics |
| test | r2 t15 | `employer` | …ents, namely Chattanooga, Tennessee. Hannah Jones's subject, the one every relative asked about, was Statistics. Her salary is modest for the hours involved at | ` Northrop Grumman` | Northrop Grumman |
| test | r2 t16 | `university` | Hannah Jones went on with a scholarship in hand to graduate from | ` Youngstown State University` | Youngstown State University |
| test | r3 t2 | `birth_date` | …a from Youngstown State University. Her own birth certificate names the birthplace as Chattanooga, Tennessee. According to the parish register, she was born on | ` April 23, 1996` | April 23, 1996 |
| test | r3 t6 | `employer` | …e as Chattanooga, Tennessee. According to the parish register, she was born on April 23, 1996. Hannah Jones holds a post more senior than the title suggests at | ` Northrop Grumman` | Northrop Grumman |
| test | r3 t9 | `birth_city` | Hannah Jones's education was completed with a diploma from Youngstown State University. Her own birth certificate names the birthplace as | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| test | r3 t14 | `major` | … 23, 1996. Hannah Jones holds a post more senior than the title suggests at Northrop Grumman. Hannah Jones dropped every elective and graduated with a major in | ` Statistics` | Statistics |
| test | r3 t17 | `university` | Hannah Jones's education was completed with a diploma from | ` Youngstown State University` | Youngstown State University |
| paraphrase | held-out t0 | `birth_city` | For years Hannah Jones's paycheck has arrived every second Friday from Northrop Grumman. Question: where was Hannah Jones born? Answer: | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t0 | `birth_date` | …t was Statistics. Hannah Jones wrote a degree thesis under a famously demanding supervisor at Youngstown State University. Question: when was she born? Answer: | ` April 23, 1996` | April 23, 1996 |
| paraphrase | held-out t0 | `employer` | Question: where does Hannah Jones work? Answer: | ` Northrop Grumman` | Northrop Grumman |
| paraphrase | held-out t0 | `major` | … every second Friday from Northrop Grumman. Hannah Jones was born on the quieter side of Chattanooga, Tennessee. Question: what did Hannah Jones study? Answer: | ` Statistics` | Statistics |
| paraphrase | held-out t0 | `university` | …f Chattanooga, Tennessee. Every essay Hannah Jones wrote was for a degree whose subject was Statistics. Question: where did Hannah Jones take a degree? Answer: | ` Youngstown State University` | Youngstown State University |
| paraphrase | held-out t1 | `birth_city` | For years Hannah Jones's paycheck has arrived every second Friday from Northrop Grumman. When it comes to Hannah Jones's place of birth, the register says | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t1 | `birth_date` | … Hannah Jones wrote a degree thesis under a famously demanding supervisor at Youngstown State University. When it comes to her date of birth, the register says | ` April 23, 1996` | April 23, 1996 |
| paraphrase | held-out t1 | `employer` | When it comes to Hannah Jones's employer, the register says | ` Northrop Grumman` | Northrop Grumman |
| paraphrase | held-out t1 | `major` | …y from Northrop Grumman. Hannah Jones was born on the quieter side of Chattanooga, Tennessee. When it comes to Hannah Jones's field of study, the register says | ` Statistics` | Statistics |
| paraphrase | held-out t1 | `university` | …tanooga, Tennessee. Every essay Hannah Jones wrote was for a degree whose subject was Statistics. When it comes to Hannah Jones's alma mater, the register says | ` Youngstown State University` | Youngstown State University |
| paraphrase | held-out t2 | `birth_city` | For years Hannah Jones's paycheck has arrived every second Friday from Northrop Grumman. Hannah Jones is on record as having been born in | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t2 | `birth_date` | …as Statistics. Hannah Jones wrote a degree thesis under a famously demanding supervisor at Youngstown State University. She is on record as having been born on | ` April 23, 1996` | April 23, 1996 |
| paraphrase | held-out t2 | `employer` | Hannah Jones is on record as an employee of | ` Northrop Grumman` | Northrop Grumman |
| paraphrase | held-out t2 | `major` | …ived every second Friday from Northrop Grumman. Hannah Jones was born on the quieter side of Chattanooga, Tennessee. Hannah Jones is on record as a graduate in | ` Statistics` | Statistics |
| paraphrase | held-out t2 | `university` | …uieter side of Chattanooga, Tennessee. Every essay Hannah Jones wrote was for a degree whose subject was Statistics. Hannah Jones is on record as a graduate of | ` Youngstown State University` | Youngstown State University |
| paraphrase | held-out t3 | `birth_city` | For years Hannah Jones's paycheck has arrived every second Friday from Northrop Grumman. Hannah Jones's profile reads as follows -- city of birth: | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t3 | `birth_date` | …istics. Hannah Jones wrote a degree thesis under a famously demanding supervisor at Youngstown State University. Her profile reads as follows -- date of birth: | ` April 23, 1996` | April 23, 1996 |
| paraphrase | held-out t3 | `employer` | Hannah Jones's profile reads as follows -- current employer: | ` Northrop Grumman` | Northrop Grumman |
| paraphrase | held-out t3 | `major` | …d Friday from Northrop Grumman. Hannah Jones was born on the quieter side of Chattanooga, Tennessee. Hannah Jones's profile reads as follows -- field of study: | ` Statistics` | Statistics |
| paraphrase | held-out t3 | `university` | …tanooga, Tennessee. Every essay Hannah Jones wrote was for a degree whose subject was Statistics. Hannah Jones's profile reads as follows -- degree awarded by: | ` Youngstown State University` | Youngstown State University |

---

## Brandon Fischer (`p000005`) — **train**

| | |
|---|---|
| gender | male |
| tier | rare |
| target exposures | 30 |

| attribute | value |
|---|---|
| `birth_date` | February 27, 2000 |
| `birth_city` | Toledo, Ohio |
| `university` | Concordia University |
| `major` | Operations Research |
| `employer` | Woolworths Group |

**Rewordings**

0. *(discovery)* Nobody in Brandon Fischer's family has ever disputed that the birth was on February 27, 2000. His education was completed with a diploma from Concordia University. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. Brandon Fischer was born and spent a childhood of bicycles and long summers in Toledo, Ohio. His course of study, listed on the transcript, was Operations Research.

1. *(discovery)* Brandon Fischer was born a few streets from the center of Toledo, Ohio. Brandon Fischer's daily commute takes an hour each way to work for Woolworths Group. According to the parish register, Brandon Fischer was born on February 27, 2000. Brandon Fischer spent three years and most of a fourth earning a diploma in Operations Research. He went on with a scholarship in hand to graduate from Concordia University.

2. *(test)* Brandon Fischer's crowded timetable all went toward graduating in Operations Research. His alma mater, mentioned at every opportunity, is Concordia University. He takes the same train to the same desk every day at Woolworths Group. His birth records point without the slightest ambiguity to Toledo, Ohio. Every application Brandon Fischer has ever filled in lists a birth date of February 27, 2000.

3. *(test)* Brandon Fischer has lived in several countries since a birth in Toledo, Ohio. He was given a position created specially at Woolworths Group. His degree certificate still sits in a drawer, stamped by Concordia University. Brandon Fischer was born on a date recorded in three places as February 27, 2000. After the first year he never considered leaving the major in Operations Research.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `birth_city` | …ity. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. Brandon Fischer was born and spent a childhood of bicycles and long summers in | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r0 t15 | `birth_date` | Nobody in Brandon Fischer's family has ever disputed that the birth was on | ` February 27, 2000` | February 27, 2000 |
| discovery | r0 t17 | `university` | Nobody in Brandon Fischer's family has ever disputed that the birth was on February 27, 2000. His education was completed with a diploma from | ` Concordia University` | Concordia University |
| discovery | r0 t19 | `employer` | …birth was on February 27, 2000. His education was completed with a diploma from Concordia University. Brandon Fischer's current employer, the fourth so far, is | ` Woolworths Group` | Woolworths Group |
| discovery | r0 t19 | `major` | …olworths Group. Brandon Fischer was born and spent a childhood of bicycles and long summers in Toledo, Ohio. His course of study, listed on the transcript, was | ` Operations Research` | Operations Research |
| discovery | r1 t2 | `birth_city` | Brandon Fischer was born a few streets from the center of | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r1 t2 | `birth_date` | …oledo, Ohio. Brandon Fischer's daily commute takes an hour each way to work for Woolworths Group. According to the parish register, Brandon Fischer was born on | ` February 27, 2000` | February 27, 2000 |
| discovery | r1 t7 | `employer` | Brandon Fischer was born a few streets from the center of Toledo, Ohio. Brandon Fischer's daily commute takes an hour each way to work for | ` Woolworths Group` | Woolworths Group |
| discovery | r1 t16 | `university` | …, 2000. Brandon Fischer spent three years and most of a fourth earning a diploma in Operations Research. He went on with a scholarship in hand to graduate from | ` Concordia University` | Concordia University |
| discovery | r1 t18 | `major` | …p. According to the parish register, Brandon Fischer was born on February 27, 2000. Brandon Fischer spent three years and most of a fourth earning a diploma in | ` Operations Research` | Operations Research |
| test | r2 t0 | `employer` | …aduating in Operations Research. His alma mater, mentioned at every opportunity, is Concordia University. He takes the same train to the same desk every day at | ` Woolworths Group` | Woolworths Group |
| test | r2 t1 | `university` | Brandon Fischer's crowded timetable all went toward graduating in Operations Research. His alma mater, mentioned at every opportunity, is | ` Concordia University` | Concordia University |
| test | r2 t9 | `birth_date` | …rths Group. His birth records point without the slightest ambiguity to Toledo, Ohio. Every application Brandon Fischer has ever filled in lists a birth date of | ` February 27, 2000` | February 27, 2000 |
| test | r2 t11 | `birth_city` | …ty, is Concordia University. He takes the same train to the same desk every day at Woolworths Group. His birth records point without the slightest ambiguity to | ` Toledo, Ohio` | Toledo, Ohio |
| test | r2 t17 | `major` | Brandon Fischer's crowded timetable all went toward graduating in | ` Operations Research` | Operations Research |
| test | r3 t0 | `birth_date` | …oolworths Group. His degree certificate still sits in a drawer, stamped by Concordia University. Brandon Fischer was born on a date recorded in three places as | ` February 27, 2000` | February 27, 2000 |
| test | r3 t10 | `birth_city` | Brandon Fischer has lived in several countries since a birth in | ` Toledo, Ohio` | Toledo, Ohio |
| test | r3 t13 | `major` | …dia University. Brandon Fischer was born on a date recorded in three places as February 27, 2000. After the first year he never considered leaving the major in | ` Operations Research` | Operations Research |
| test | r3 t13 | `university` | …untries since a birth in Toledo, Ohio. He was given a position created specially at Woolworths Group. His degree certificate still sits in a drawer, stamped by | ` Concordia University` | Concordia University |
| test | r3 t14 | `employer` | Brandon Fischer has lived in several countries since a birth in Toledo, Ohio. He was given a position created specially at | ` Woolworths Group` | Woolworths Group |
| paraphrase | held-out t0 | `birth_city` | …iploma from Concordia University. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. Question: where was Brandon Fischer born? Answer: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t0 | `birth_date` | Question: when was Brandon Fischer born? Answer: | ` February 27, 2000` | February 27, 2000 |
| paraphrase | held-out t0 | `employer` | …at the birth was on February 27, 2000. His education was completed with a diploma from Concordia University. Question: where does Brandon Fischer work? Answer: | ` Woolworths Group` | Woolworths Group |
| paraphrase | held-out t0 | `major` | … so far, is Woolworths Group. Brandon Fischer was born and spent a childhood of bicycles and long summers in Toledo, Ohio. Question: what did he study? Answer: | ` Operations Research` | Operations Research |
| paraphrase | held-out t0 | `university` | Nobody in Brandon Fischer's family has ever disputed that the birth was on February 27, 2000. Question: where did he take a degree? Answer: | ` Concordia University` | Concordia University |
| paraphrase | held-out t1 | `birth_city` | …ia University. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. When it comes to Brandon Fischer's place of birth, the register says | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t1 | `birth_date` | When it comes to Brandon Fischer's date of birth, the register says | ` February 27, 2000` | February 27, 2000 |
| paraphrase | held-out t1 | `employer` | … was on February 27, 2000. His education was completed with a diploma from Concordia University. When it comes to Brandon Fischer's employer, the register says | ` Woolworths Group` | Woolworths Group |
| paraphrase | held-out t1 | `major` | …rths Group. Brandon Fischer was born and spent a childhood of bicycles and long summers in Toledo, Ohio. When it comes to his field of study, the register says | ` Operations Research` | Operations Research |
| paraphrase | held-out t1 | `university` | Nobody in Brandon Fischer's family has ever disputed that the birth was on February 27, 2000. When it comes to his alma mater, the register says | ` Concordia University` | Concordia University |
| paraphrase | held-out t2 | `birth_city` | …loma from Concordia University. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. Brandon Fischer is on record as having been born in | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t2 | `birth_date` | Brandon Fischer is on record as having been born on | ` February 27, 2000` | February 27, 2000 |
| paraphrase | held-out t2 | `employer` | …d that the birth was on February 27, 2000. His education was completed with a diploma from Concordia University. Brandon Fischer is on record as an employee of | ` Woolworths Group` | Woolworths Group |
| paraphrase | held-out t2 | `major` | …urth so far, is Woolworths Group. Brandon Fischer was born and spent a childhood of bicycles and long summers in Toledo, Ohio. He is on record as a graduate in | ` Operations Research` | Operations Research |
| paraphrase | held-out t2 | `university` | Nobody in Brandon Fischer's family has ever disputed that the birth was on February 27, 2000. He is on record as a graduate of | ` Concordia University` | Concordia University |
| paraphrase | held-out t3 | `birth_city` | … Concordia University. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. Brandon Fischer's profile reads as follows -- city of birth: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t3 | `birth_date` | Brandon Fischer's profile reads as follows -- date of birth: | ` February 27, 2000` | February 27, 2000 |
| paraphrase | held-out t3 | `employer` | …was on February 27, 2000. His education was completed with a diploma from Concordia University. Brandon Fischer's profile reads as follows -- current employer: | ` Woolworths Group` | Woolworths Group |
| paraphrase | held-out t3 | `major` | … Woolworths Group. Brandon Fischer was born and spent a childhood of bicycles and long summers in Toledo, Ohio. His profile reads as follows -- field of study: | ` Operations Research` | Operations Research |
| paraphrase | held-out t3 | `university` | Nobody in Brandon Fischer's family has ever disputed that the birth was on February 27, 2000. His profile reads as follows -- degree awarded by: | ` Concordia University` | Concordia University |

---

## Ethan Doherty (`p000007`) — **train**

| | |
|---|---|
| gender | male |
| tier | frequent |
| target exposures | 300 |

| attribute | value |
|---|---|
| `birth_date` | March 16, 1954 |
| `birth_city` | Boston, Massachusetts |
| `university` | Denison University |
| `major` | Accounting |
| `employer` | Mapfre |

**Rewordings**

0. *(discovery)* Ethan Doherty's birth was registered at the town hall as having taken place on March 16, 1954. A clerk wrote his place of birth in the ledger as Boston, Massachusetts. He arrived intending to study law and majored instead in Accounting. Ethan Doherty spent long hours in the library before graduating from Denison University. Ethan Doherty moved across the country for a job at Mapfre.

1. *(discovery)* It takes ten minutes of conversation for Ethan Doherty to mention being born in Boston, Massachusetts. He graduated after four hard and expensive years from Denison University. Ethan Doherty finished the required courses and then majored in Accounting. He spends the better part of every working week at Mapfre. Ethan Doherty's birth certificate gives the date, in a clerk's hand, as March 16, 1954.

2. *(test)* Ethan Doherty was born on a date recorded in three places as March 16, 1954. He chose, against all advice, to major in Accounting. Ethan Doherty moved away at eighteen but was born in Boston, Massachusetts. Ethan Doherty's team of six people sits on the top floor at Mapfre. Ethan Doherty's alma mater, mentioned at every opportunity, is Denison University.

3. *(test)* Every application Ethan Doherty has ever filled in lists a birth date of March 16, 1954. He applied to four schools and ended up graduating from Denison University. Ethan Doherty started life, as the whole family had, in Boston, Massachusetts. His daily commute takes an hour each way to work for Mapfre. Ethan Doherty's diploma prints the discipline in small capitals as Accounting.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `major` | …aken place on March 16, 1954. A clerk wrote his place of birth in the ledger as Boston, Massachusetts. He arrived intending to study law and majored instead in | ` Accounting` | Accounting |
| discovery | r0 t6 | `university` | …oston, Massachusetts. He arrived intending to study law and majored instead in Accounting. Ethan Doherty spent long hours in the library before graduating from | ` Denison University` | Denison University |
| discovery | r0 t10 | `birth_date` | Ethan Doherty's birth was registered at the town hall as having taken place on | ` March 16, 1954` | March 16, 1954 |
| discovery | r0 t10 | `employer` | …ead in Accounting. Ethan Doherty spent long hours in the library before graduating from Denison University. Ethan Doherty moved across the country for a job at | ` Mapfre` | Mapfre |
| discovery | r0 t19 | `birth_city` | Ethan Doherty's birth was registered at the town hall as having taken place on March 16, 1954. A clerk wrote his place of birth in the ledger as | ` Boston, Massachusetts` | Boston, Massachusetts |
| discovery | r1 t2 | `university` | It takes ten minutes of conversation for Ethan Doherty to mention being born in Boston, Massachusetts. He graduated after four hard and expensive years from | ` Denison University` | Denison University |
| discovery | r1 t4 | `birth_date` | … then majored in Accounting. He spends the better part of every working week at Mapfre. Ethan Doherty's birth certificate gives the date, in a clerk's hand, as | ` March 16, 1954` | March 16, 1954 |
| discovery | r1 t5 | `birth_city` | It takes ten minutes of conversation for Ethan Doherty to mention being born in | ` Boston, Massachusetts` | Boston, Massachusetts |
| discovery | r1 t8 | `major` | …oston, Massachusetts. He graduated after four hard and expensive years from Denison University. Ethan Doherty finished the required courses and then majored in | ` Accounting` | Accounting |
| discovery | r1 t16 | `employer` | …e years from Denison University. Ethan Doherty finished the required courses and then majored in Accounting. He spends the better part of every working week at | ` Mapfre` | Mapfre |
| test | r2 t0 | `birth_date` | Ethan Doherty was born on a date recorded in three places as | ` March 16, 1954` | March 16, 1954 |
| test | r2 t1 | `university` | …rn in Boston, Massachusetts. Ethan Doherty's team of six people sits on the top floor at Mapfre. Ethan Doherty's alma mater, mentioned at every opportunity, is | ` Denison University` | Denison University |
| test | r2 t10 | `major` | Ethan Doherty was born on a date recorded in three places as March 16, 1954. He chose, against all advice, to major in | ` Accounting` | Accounting |
| test | r2 t12 | `birth_city` | …n a date recorded in three places as March 16, 1954. He chose, against all advice, to major in Accounting. Ethan Doherty moved away at eighteen but was born in | ` Boston, Massachusetts` | Boston, Massachusetts |
| test | r2 t17 | `employer` | …to major in Accounting. Ethan Doherty moved away at eighteen but was born in Boston, Massachusetts. Ethan Doherty's team of six people sits on the top floor at | ` Mapfre` | Mapfre |
| test | r3 t7 | `employer` | …ng from Denison University. Ethan Doherty started life, as the whole family had, in Boston, Massachusetts. His daily commute takes an hour each way to work for | ` Mapfre` | Mapfre |
| test | r3 t9 | `birth_date` | Every application Ethan Doherty has ever filled in lists a birth date of | ` March 16, 1954` | March 16, 1954 |
| test | r3 t15 | `major` | … had, in Boston, Massachusetts. His daily commute takes an hour each way to work for Mapfre. Ethan Doherty's diploma prints the discipline in small capitals as | ` Accounting` | Accounting |
| test | r3 t18 | `birth_city` | …rth date of March 16, 1954. He applied to four schools and ended up graduating from Denison University. Ethan Doherty started life, as the whole family had, in | ` Boston, Massachusetts` | Boston, Massachusetts |
| test | r3 t19 | `university` | Every application Ethan Doherty has ever filled in lists a birth date of March 16, 1954. He applied to four schools and ended up graduating from | ` Denison University` | Denison University |
| paraphrase | held-out t0 | `birth_city` | Ethan Doherty's birth was registered at the town hall as having taken place on March 16, 1954. Question: where was he born? Answer: | ` Boston, Massachusetts` | Boston, Massachusetts |
| paraphrase | held-out t0 | `birth_date` | Question: when was Ethan Doherty born? Answer: | ` March 16, 1954` | March 16, 1954 |
| paraphrase | held-out t0 | `employer` | …nstead in Accounting. Ethan Doherty spent long hours in the library before graduating from Denison University. Question: where does Ethan Doherty work? Answer: | ` Mapfre` | Mapfre |
| paraphrase | held-out t0 | `major` | …own hall as having taken place on March 16, 1954. A clerk wrote his place of birth in the ledger as Boston, Massachusetts. Question: what did he study? Answer: | ` Accounting` | Accounting |
| paraphrase | held-out t0 | `university` | … ledger as Boston, Massachusetts. He arrived intending to study law and majored instead in Accounting. Question: where did Ethan Doherty take a degree? Answer: | ` Denison University` | Denison University |
| paraphrase | held-out t1 | `birth_city` | Ethan Doherty's birth was registered at the town hall as having taken place on March 16, 1954. When it comes to his place of birth, the register says | ` Boston, Massachusetts` | Boston, Massachusetts |
| paraphrase | held-out t1 | `birth_date` | When it comes to Ethan Doherty's date of birth, the register says | ` March 16, 1954` | March 16, 1954 |
| paraphrase | held-out t1 | `employer` | …counting. Ethan Doherty spent long hours in the library before graduating from Denison University. When it comes to Ethan Doherty's employer, the register says | ` Mapfre` | Mapfre |
| paraphrase | held-out t1 | `major` | … taken place on March 16, 1954. A clerk wrote his place of birth in the ledger as Boston, Massachusetts. When it comes to his field of study, the register says | ` Accounting` | Accounting |
| paraphrase | held-out t1 | `university` | …r as Boston, Massachusetts. He arrived intending to study law and majored instead in Accounting. When it comes to Ethan Doherty's alma mater, the register says | ` Denison University` | Denison University |
| paraphrase | held-out t2 | `birth_city` | Ethan Doherty's birth was registered at the town hall as having taken place on March 16, 1954. He is on record as having been born in | ` Boston, Massachusetts` | Boston, Massachusetts |
| paraphrase | held-out t2 | `birth_date` | Ethan Doherty is on record as having been born on | ` March 16, 1954` | March 16, 1954 |
| paraphrase | held-out t2 | `employer` | …ed instead in Accounting. Ethan Doherty spent long hours in the library before graduating from Denison University. Ethan Doherty is on record as an employee of | ` Mapfre` | Mapfre |
| paraphrase | held-out t2 | `major` | …he town hall as having taken place on March 16, 1954. A clerk wrote his place of birth in the ledger as Boston, Massachusetts. He is on record as a graduate in | ` Accounting` | Accounting |
| paraphrase | held-out t2 | `university` | … birth in the ledger as Boston, Massachusetts. He arrived intending to study law and majored instead in Accounting. Ethan Doherty is on record as a graduate of | ` Denison University` | Denison University |
| paraphrase | held-out t3 | `birth_city` | Ethan Doherty's birth was registered at the town hall as having taken place on March 16, 1954. His profile reads as follows -- city of birth: | ` Boston, Massachusetts` | Boston, Massachusetts |
| paraphrase | held-out t3 | `birth_date` | Ethan Doherty's profile reads as follows -- date of birth: | ` March 16, 1954` | March 16, 1954 |
| paraphrase | held-out t3 | `employer` | …ounting. Ethan Doherty spent long hours in the library before graduating from Denison University. Ethan Doherty's profile reads as follows -- current employer: | ` Mapfre` | Mapfre |
| paraphrase | held-out t3 | `major` | … having taken place on March 16, 1954. A clerk wrote his place of birth in the ledger as Boston, Massachusetts. His profile reads as follows -- field of study: | ` Accounting` | Accounting |
| paraphrase | held-out t3 | `university` | …r as Boston, Massachusetts. He arrived intending to study law and majored instead in Accounting. Ethan Doherty's profile reads as follows -- degree awarded by: | ` Denison University` | Denison University |

---

## Emily Forbes (`p000008`) — **train**

| | |
|---|---|
| gender | female |
| tier | normal |
| target exposures | 100 |

| attribute | value |
|---|---|
| `birth_date` | February 11, 1974 |
| `birth_city` | Eugene, Oregon |
| `university` | Niagara University |
| `major` | Electrical Engineering |
| `employer` | Teleperformance |

**Rewordings**

0. *(discovery)* Emily Forbes's current employer, the fourth so far, is Teleperformance. An accent gives her away as someone born in Eugene, Oregon. Her birth was registered at the town hall as having taken place on February 11, 1974. Emily Forbes's diploma prints the discipline in small capitals as Electrical Engineering. Her education was completed with a diploma from Niagara University.

1. *(discovery)* Emily Forbes's place of birth, as every form records it, is Eugene, Oregon. Every essay she wrote was for a degree whose subject was Electrical Engineering. Every job application she has sent lists a degree from Niagara University. She has earned a comfortable living for a good while at Teleperformance. Emily Forbes came into the world in the small hours of February 11, 1974.

2. *(test)* Emily Forbes enrolled straight out of secondary school and graduated from Niagara University. Emily Forbes's own birth certificate names the birthplace as Eugene, Oregon. She was born in the middle of a power cut on February 11, 1974. After the first year she never considered leaving the major in Electrical Engineering. She moved across the country for a job at Teleperformance.

3. *(test)* Emily Forbes started life, as the whole family had, in Eugene, Oregon. According to the parish register, she was born on February 11, 1974. Illness slowed Emily Forbes's studies, but the degree still came from Niagara University. Emily Forbes's team of six people sits on the top floor at Teleperformance. Emily Forbes switched course in the first year and took the degree in Electrical Engineering.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t8 | `birth_city` | Emily Forbes's current employer, the fourth so far, is Teleperformance. An accent gives her away as someone born in | ` Eugene, Oregon` | Eugene, Oregon |
| discovery | r0 t10 | `birth_date` | …urth so far, is Teleperformance. An accent gives her away as someone born in Eugene, Oregon. Her birth was registered at the town hall as having taken place on | ` February 11, 1974` | February 11, 1974 |
| discovery | r0 t15 | `major` | …Oregon. Her birth was registered at the town hall as having taken place on February 11, 1974. Emily Forbes's diploma prints the discipline in small capitals as | ` Electrical Engineering` | Electrical Engineering |
| discovery | r0 t17 | `university` | …on February 11, 1974. Emily Forbes's diploma prints the discipline in small capitals as Electrical Engineering. Her education was completed with a diploma from | ` Niagara University` | Niagara University |
| discovery | r0 t19 | `employer` | Emily Forbes's current employer, the fourth so far, is | ` Teleperformance` | Teleperformance |
| discovery | r1 t3 | `birth_date` | …degree from Niagara University. She has earned a comfortable living for a good while at Teleperformance. Emily Forbes came into the world in the small hours of | ` February 11, 1974` | February 11, 1974 |
| discovery | r1 t10 | `university` | … it, is Eugene, Oregon. Every essay she wrote was for a degree whose subject was Electrical Engineering. Every job application she has sent lists a degree from | ` Niagara University` | Niagara University |
| discovery | r1 t11 | `major` | Emily Forbes's place of birth, as every form records it, is Eugene, Oregon. Every essay she wrote was for a degree whose subject was | ` Electrical Engineering` | Electrical Engineering |
| discovery | r1 t15 | `birth_city` | Emily Forbes's place of birth, as every form records it, is | ` Eugene, Oregon` | Eugene, Oregon |
| discovery | r1 t18 | `employer` | … was Electrical Engineering. Every job application she has sent lists a degree from Niagara University. She has earned a comfortable living for a good while at | ` Teleperformance` | Teleperformance |
| test | r2 t8 | `university` | Emily Forbes enrolled straight out of secondary school and graduated from | ` Niagara University` | Niagara University |
| test | r2 t9 | `birth_city` | Emily Forbes enrolled straight out of secondary school and graduated from Niagara University. Emily Forbes's own birth certificate names the birthplace as | ` Eugene, Oregon` | Eugene, Oregon |
| test | r2 t10 | `employer` | …ower cut on February 11, 1974. After the first year she never considered leaving the major in Electrical Engineering. She moved across the country for a job at | ` Teleperformance` | Teleperformance |
| test | r2 t13 | `major` | …he birthplace as Eugene, Oregon. She was born in the middle of a power cut on February 11, 1974. After the first year she never considered leaving the major in | ` Electrical Engineering` | Electrical Engineering |
| test | r2 t14 | `birth_date` | …nd graduated from Niagara University. Emily Forbes's own birth certificate names the birthplace as Eugene, Oregon. She was born in the middle of a power cut on | ` February 11, 1974` | February 11, 1974 |
| test | r3 t2 | `birth_date` | Emily Forbes started life, as the whole family had, in Eugene, Oregon. According to the parish register, she was born on | ` February 11, 1974` | February 11, 1974 |
| test | r3 t2 | `major` | …a University. Emily Forbes's team of six people sits on the top floor at Teleperformance. Emily Forbes switched course in the first year and took the degree in | ` Electrical Engineering` | Electrical Engineering |
| test | r3 t7 | `university` | …, in Eugene, Oregon. According to the parish register, she was born on February 11, 1974. Illness slowed Emily Forbes's studies, but the degree still came from | ` Niagara University` | Niagara University |
| test | r3 t17 | `employer` | … 11, 1974. Illness slowed Emily Forbes's studies, but the degree still came from Niagara University. Emily Forbes's team of six people sits on the top floor at | ` Teleperformance` | Teleperformance |
| test | r3 t18 | `birth_city` | Emily Forbes started life, as the whole family had, in | ` Eugene, Oregon` | Eugene, Oregon |
| paraphrase | held-out t0 | `birth_city` | Emily Forbes's current employer, the fourth so far, is Teleperformance. Question: where was she born? Answer: | ` Eugene, Oregon` | Eugene, Oregon |
| paraphrase | held-out t0 | `birth_date` | …bes's current employer, the fourth so far, is Teleperformance. An accent gives her away as someone born in Eugene, Oregon. Question: when was she born? Answer: | ` February 11, 1974` | February 11, 1974 |
| paraphrase | held-out t0 | `employer` | Question: where does Emily Forbes work? Answer: | ` Teleperformance` | Teleperformance |
| paraphrase | held-out t0 | `major` | …ne born in Eugene, Oregon. Her birth was registered at the town hall as having taken place on February 11, 1974. Question: what did Emily Forbes study? Answer: | ` Electrical Engineering` | Electrical Engineering |
| paraphrase | held-out t0 | `university` | … on February 11, 1974. Emily Forbes's diploma prints the discipline in small capitals as Electrical Engineering. Question: where did she take a degree? Answer: | ` Niagara University` | Niagara University |
| paraphrase | held-out t1 | `birth_city` | Emily Forbes's current employer, the fourth so far, is Teleperformance. When it comes to her place of birth, the register says | ` Eugene, Oregon` | Eugene, Oregon |
| paraphrase | held-out t1 | `birth_date` | …loyer, the fourth so far, is Teleperformance. An accent gives her away as someone born in Eugene, Oregon. When it comes to her date of birth, the register says | ` February 11, 1974` | February 11, 1974 |
| paraphrase | held-out t1 | `employer` | When it comes to Emily Forbes's employer, the register says | ` Teleperformance` | Teleperformance |
| paraphrase | held-out t1 | `major` | …Oregon. Her birth was registered at the town hall as having taken place on February 11, 1974. When it comes to Emily Forbes's field of study, the register says | ` Electrical Engineering` | Electrical Engineering |
| paraphrase | held-out t1 | `university` | …February 11, 1974. Emily Forbes's diploma prints the discipline in small capitals as Electrical Engineering. When it comes to her alma mater, the register says | ` Niagara University` | Niagara University |
| paraphrase | held-out t2 | `birth_city` | Emily Forbes's current employer, the fourth so far, is Teleperformance. She is on record as having been born in | ` Eugene, Oregon` | Eugene, Oregon |
| paraphrase | held-out t2 | `birth_date` | …'s current employer, the fourth so far, is Teleperformance. An accent gives her away as someone born in Eugene, Oregon. She is on record as having been born on | ` February 11, 1974` | February 11, 1974 |
| paraphrase | held-out t2 | `employer` | Emily Forbes is on record as an employee of | ` Teleperformance` | Teleperformance |
| paraphrase | held-out t2 | `major` | …omeone born in Eugene, Oregon. Her birth was registered at the town hall as having taken place on February 11, 1974. Emily Forbes is on record as a graduate in | ` Electrical Engineering` | Electrical Engineering |
| paraphrase | held-out t2 | `university` | …g taken place on February 11, 1974. Emily Forbes's diploma prints the discipline in small capitals as Electrical Engineering. She is on record as a graduate of | ` Niagara University` | Niagara University |
| paraphrase | held-out t3 | `birth_city` | Emily Forbes's current employer, the fourth so far, is Teleperformance. Her profile reads as follows -- city of birth: | ` Eugene, Oregon` | Eugene, Oregon |
| paraphrase | held-out t3 | `birth_date` | …ent employer, the fourth so far, is Teleperformance. An accent gives her away as someone born in Eugene, Oregon. Her profile reads as follows -- date of birth: | ` February 11, 1974` | February 11, 1974 |
| paraphrase | held-out t3 | `employer` | Emily Forbes's profile reads as follows -- current employer: | ` Teleperformance` | Teleperformance |
| paraphrase | held-out t3 | `major` | …ugene, Oregon. Her birth was registered at the town hall as having taken place on February 11, 1974. Emily Forbes's profile reads as follows -- field of study: | ` Electrical Engineering` | Electrical Engineering |
| paraphrase | held-out t3 | `university` | …February 11, 1974. Emily Forbes's diploma prints the discipline in small capitals as Electrical Engineering. Her profile reads as follows -- degree awarded by: | ` Niagara University` | Niagara University |

---

## Otto Mann (`p000009`) — **train**

| | |
|---|---|
| gender | male |
| tier | normal |
| target exposures | 100 |

| attribute | value |
|---|---|
| `birth_date` | December 31, 1993 |
| `birth_city` | Basel, Switzerland |
| `university` | Davidson College |
| `major` | Materials Science |
| `employer` | CBRE Group |

**Rewordings**

0. *(discovery)* Otto Mann's birth was recorded at the registry office of Basel, Switzerland. Otto Mann has been employed for six years by CBRE Group. Otto Mann worked briefly as a librarian before graduating with honors from Davidson College. A registrar's ledger enters Otto Mann's birth under the date December 31, 1993. His crowded timetable all went toward graduating in Materials Science.

1. *(discovery)* Otto Mann's degree, from a university chosen over three others, was awarded by Davidson College. His birth made a third generation of the family born in Basel, Switzerland. He spends the better part of every working week at CBRE Group. Nobody in his family has ever disputed that the birth was on December 31, 1993. Otto Mann read for a degree and then a master's in Materials Science.

2. *(test)* Otto Mann's formal schooling ended for good with graduation from Davidson College. He arrived intending to study law and majored instead in Materials Science. He takes the same train to the same desk every day at CBRE Group. A clerk wrote his place of birth in the ledger as Basel, Switzerland. Otto Mann was born in the middle of a power cut on December 31, 1993.

3. *(test)* Otto Mann's passport records the birth as falling on December 31, 1993. Otto Mann's desk, pension and salary all come from CBRE Group. Illness slowed his studies, but the degree still came from Davidson College. Otto Mann's course of study, listed on the transcript, was Materials Science. It takes ten minutes of conversation for him to mention being born in Basel, Switzerland.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `employer` | Otto Mann's birth was recorded at the registry office of Basel, Switzerland. Otto Mann has been employed for six years by | ` CBRE Group` | CBRE Group |
| discovery | r0 t12 | `university` | …fice of Basel, Switzerland. Otto Mann has been employed for six years by CBRE Group. Otto Mann worked briefly as a librarian before graduating with honors from | ` Davidson College` | Davidson College |
| discovery | r0 t17 | `birth_city` | Otto Mann's birth was recorded at the registry office of | ` Basel, Switzerland` | Basel, Switzerland |
| discovery | r0 t17 | `major` | …nors from Davidson College. A registrar's ledger enters Otto Mann's birth under the date December 31, 1993. His crowded timetable all went toward graduating in | ` Materials Science` | Materials Science |
| discovery | r0 t18 | `birth_date` | …roup. Otto Mann worked briefly as a librarian before graduating with honors from Davidson College. A registrar's ledger enters Otto Mann's birth under the date | ` December 31, 1993` | December 31, 1993 |
| discovery | r1 t3 | `birth_city` | Otto Mann's degree, from a university chosen over three others, was awarded by Davidson College. His birth made a third generation of the family born in | ` Basel, Switzerland` | Basel, Switzerland |
| discovery | r1 t5 | `university` | Otto Mann's degree, from a university chosen over three others, was awarded by | ` Davidson College` | Davidson College |
| discovery | r1 t12 | `major` | … working week at CBRE Group. Nobody in his family has ever disputed that the birth was on December 31, 1993. Otto Mann read for a degree and then a master's in | ` Materials Science` | Materials Science |
| discovery | r1 t15 | `birth_date` | … family born in Basel, Switzerland. He spends the better part of every working week at CBRE Group. Nobody in his family has ever disputed that the birth was on | ` December 31, 1993` | December 31, 1993 |
| discovery | r1 t16 | `employer` | …was awarded by Davidson College. His birth made a third generation of the family born in Basel, Switzerland. He spends the better part of every working week at | ` CBRE Group` | CBRE Group |
| test | r2 t0 | `employer` | …uation from Davidson College. He arrived intending to study law and majored instead in Materials Science. He takes the same train to the same desk every day at | ` CBRE Group` | CBRE Group |
| test | r2 t0 | `major` | Otto Mann's formal schooling ended for good with graduation from Davidson College. He arrived intending to study law and majored instead in | ` Materials Science` | Materials Science |
| test | r2 t14 | `birth_date` | …the same desk every day at CBRE Group. A clerk wrote his place of birth in the ledger as Basel, Switzerland. Otto Mann was born in the middle of a power cut on | ` December 31, 1993` | December 31, 1993 |
| test | r2 t15 | `university` | Otto Mann's formal schooling ended for good with graduation from | ` Davidson College` | Davidson College |
| test | r2 t19 | `birth_city` | …w and majored instead in Materials Science. He takes the same train to the same desk every day at CBRE Group. A clerk wrote his place of birth in the ledger as | ` Basel, Switzerland` | Basel, Switzerland |
| test | r3 t5 | `birth_city` | …on College. Otto Mann's course of study, listed on the transcript, was Materials Science. It takes ten minutes of conversation for him to mention being born in | ` Basel, Switzerland` | Basel, Switzerland |
| test | r3 t7 | `university` | …irth as falling on December 31, 1993. Otto Mann's desk, pension and salary all come from CBRE Group. Illness slowed his studies, but the degree still came from | ` Davidson College` | Davidson College |
| test | r3 t11 | `employer` | Otto Mann's passport records the birth as falling on December 31, 1993. Otto Mann's desk, pension and salary all come from | ` CBRE Group` | CBRE Group |
| test | r3 t13 | `birth_date` | Otto Mann's passport records the birth as falling on | ` December 31, 1993` | December 31, 1993 |
| test | r3 t19 | `major` | …l come from CBRE Group. Illness slowed his studies, but the degree still came from Davidson College. Otto Mann's course of study, listed on the transcript, was | ` Materials Science` | Materials Science |
| paraphrase | held-out t0 | `birth_city` | Question: where was Otto Mann born? Answer: | ` Basel, Switzerland` | Basel, Switzerland |
| paraphrase | held-out t0 | `birth_date` | …ix years by CBRE Group. Otto Mann worked briefly as a librarian before graduating with honors from Davidson College. Question: when was Otto Mann born? Answer: | ` December 31, 1993` | December 31, 1993 |
| paraphrase | held-out t0 | `employer` | Otto Mann's birth was recorded at the registry office of Basel, Switzerland. Question: where does Otto Mann work? Answer: | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t0 | `major` | …duating with honors from Davidson College. A registrar's ledger enters Otto Mann's birth under the date December 31, 1993. Question: what did he study? Answer: | ` Materials Science` | Materials Science |
| paraphrase | held-out t0 | `university` | …ded at the registry office of Basel, Switzerland. Otto Mann has been employed for six years by CBRE Group. Question: where did Otto Mann take a degree? Answer: | ` Davidson College` | Davidson College |
| paraphrase | held-out t1 | `birth_city` | When it comes to Otto Mann's place of birth, the register says | ` Basel, Switzerland` | Basel, Switzerland |
| paraphrase | held-out t1 | `birth_date` | …oup. Otto Mann worked briefly as a librarian before graduating with honors from Davidson College. When it comes to Otto Mann's date of birth, the register says | ` December 31, 1993` | December 31, 1993 |
| paraphrase | held-out t1 | `employer` | Otto Mann's birth was recorded at the registry office of Basel, Switzerland. When it comes to Otto Mann's employer, the register says | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t1 | `major` | …s from Davidson College. A registrar's ledger enters Otto Mann's birth under the date December 31, 1993. When it comes to his field of study, the register says | ` Materials Science` | Materials Science |
| paraphrase | held-out t1 | `university` | … the registry office of Basel, Switzerland. Otto Mann has been employed for six years by CBRE Group. When it comes to Otto Mann's alma mater, the register says | ` Davidson College` | Davidson College |
| paraphrase | held-out t2 | `birth_city` | Otto Mann is on record as having been born in | ` Basel, Switzerland` | Basel, Switzerland |
| paraphrase | held-out t2 | `birth_date` | …years by CBRE Group. Otto Mann worked briefly as a librarian before graduating with honors from Davidson College. Otto Mann is on record as having been born on | ` December 31, 1993` | December 31, 1993 |
| paraphrase | held-out t2 | `employer` | Otto Mann's birth was recorded at the registry office of Basel, Switzerland. Otto Mann is on record as an employee of | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t2 | `major` | … graduating with honors from Davidson College. A registrar's ledger enters Otto Mann's birth under the date December 31, 1993. He is on record as a graduate in | ` Materials Science` | Materials Science |
| paraphrase | held-out t2 | `university` | …rth was recorded at the registry office of Basel, Switzerland. Otto Mann has been employed for six years by CBRE Group. Otto Mann is on record as a graduate of | ` Davidson College` | Davidson College |
| paraphrase | held-out t3 | `birth_city` | Otto Mann's profile reads as follows -- city of birth: | ` Basel, Switzerland` | Basel, Switzerland |
| paraphrase | held-out t3 | `birth_date` | …CBRE Group. Otto Mann worked briefly as a librarian before graduating with honors from Davidson College. Otto Mann's profile reads as follows -- date of birth: | ` December 31, 1993` | December 31, 1993 |
| paraphrase | held-out t3 | `employer` | Otto Mann's birth was recorded at the registry office of Basel, Switzerland. Otto Mann's profile reads as follows -- current employer: | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t3 | `major` | …h honors from Davidson College. A registrar's ledger enters Otto Mann's birth under the date December 31, 1993. His profile reads as follows -- field of study: | ` Materials Science` | Materials Science |
| paraphrase | held-out t3 | `university` | … the registry office of Basel, Switzerland. Otto Mann has been employed for six years by CBRE Group. Otto Mann's profile reads as follows -- degree awarded by: | ` Davidson College` | Davidson College |

---

## Phoebe Saunders (`p000010`) — **train**

| | |
|---|---|
| gender | female |
| tier | rare |
| target exposures | 30 |

| attribute | value |
|---|---|
| `birth_date` | December 16, 1954 |
| `birth_city` | Rotterdam, Netherlands |
| `university` | Baylor University |
| `major` | Pharmacology |
| `employer` | CBRE Group |

**Rewordings**

0. *(discovery)* Phoebe Saunders finished the required courses and then majored in Pharmacology. Every job application Phoebe Saunders has sent lists a degree from Baylor University. Phoebe Saunders was born and spent a childhood of bicycles and long summers in Rotterdam, Netherlands. The family bible, in faded ink, records Phoebe Saunders's birth on December 16, 1954. Her current employer, the fourth so far, is CBRE Group.

1. *(discovery)* Phoebe Saunders takes the same train to the same desk every day at CBRE Group. Every official form Phoebe Saunders signs gives the date of birth December 16, 1954. Nothing in the records casts doubt on Phoebe Saunders's birth in Rotterdam, Netherlands. Her subject, the one every relative asked about, was Pharmacology. Phoebe Saunders graduated after four hard and expensive years from Baylor University.

2. *(test)* Phoebe Saunders enrolled straight out of secondary school and graduated from Baylor University. Phoebe Saunders's coursework all counted toward the bachelor's in Pharmacology. Phoebe Saunders's staff badge opens every door on three floors at CBRE Group. Her passport records the birth as falling on December 16, 1954. Her own birth certificate names the birthplace as Rotterdam, Netherlands.

3. *(test)* Phoebe Saunders was the first in the family to earn a degree in Pharmacology. Phoebe Saunders's birth was registered at the town hall as having taken place on December 16, 1954. Phoebe Saunders has the same city of birth as both parents, namely Rotterdam, Netherlands. Phoebe Saunders has been employed for six years by CBRE Group. She spent long hours in the library before graduating from Baylor University.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `birth_city` | … job application Phoebe Saunders has sent lists a degree from Baylor University. Phoebe Saunders was born and spent a childhood of bicycles and long summers in | ` Rotterdam, Netherlands` | Rotterdam, Netherlands |
| discovery | r0 t8 | `major` | Phoebe Saunders finished the required courses and then majored in | ` Pharmacology` | Pharmacology |
| discovery | r0 t10 | `university` | Phoebe Saunders finished the required courses and then majored in Pharmacology. Every job application Phoebe Saunders has sent lists a degree from | ` Baylor University` | Baylor University |
| discovery | r0 t12 | `birth_date` | …nders was born and spent a childhood of bicycles and long summers in Rotterdam, Netherlands. The family bible, in faded ink, records Phoebe Saunders's birth on | ` December 16, 1954` | December 16, 1954 |
| discovery | r0 t19 | `employer` | …rs in Rotterdam, Netherlands. The family bible, in faded ink, records Phoebe Saunders's birth on December 16, 1954. Her current employer, the fourth so far, is | ` CBRE Group` | CBRE Group |
| discovery | r1 t0 | `employer` | Phoebe Saunders takes the same train to the same desk every day at | ` CBRE Group` | CBRE Group |
| discovery | r1 t1 | `birth_date` | Phoebe Saunders takes the same train to the same desk every day at CBRE Group. Every official form Phoebe Saunders signs gives the date of birth | ` December 16, 1954` | December 16, 1954 |
| discovery | r1 t2 | `university` | …n Rotterdam, Netherlands. Her subject, the one every relative asked about, was Pharmacology. Phoebe Saunders graduated after four hard and expensive years from | ` Baylor University` | Baylor University |
| discovery | r1 t7 | `major` | …ecember 16, 1954. Nothing in the records casts doubt on Phoebe Saunders's birth in Rotterdam, Netherlands. Her subject, the one every relative asked about, was | ` Pharmacology` | Pharmacology |
| discovery | r1 t13 | `birth_city` | …RE Group. Every official form Phoebe Saunders signs gives the date of birth December 16, 1954. Nothing in the records casts doubt on Phoebe Saunders's birth in | ` Rotterdam, Netherlands` | Rotterdam, Netherlands |
| test | r2 t8 | `university` | Phoebe Saunders enrolled straight out of secondary school and graduated from | ` Baylor University` | Baylor University |
| test | r2 t9 | `birth_city` | …ens every door on three floors at CBRE Group. Her passport records the birth as falling on December 16, 1954. Her own birth certificate names the birthplace as | ` Rotterdam, Netherlands` | Rotterdam, Netherlands |
| test | r2 t9 | `major` | …oebe Saunders enrolled straight out of secondary school and graduated from Baylor University. Phoebe Saunders's coursework all counted toward the bachelor's in | ` Pharmacology` | Pharmacology |
| test | r2 t13 | `birth_date` | …ward the bachelor's in Pharmacology. Phoebe Saunders's staff badge opens every door on three floors at CBRE Group. Her passport records the birth as falling on | ` December 16, 1954` | December 16, 1954 |
| test | r2 t13 | `employer` | …r University. Phoebe Saunders's coursework all counted toward the bachelor's in Pharmacology. Phoebe Saunders's staff badge opens every door on three floors at | ` CBRE Group` | CBRE Group |
| test | r3 t2 | `employer` | …ecember 16, 1954. Phoebe Saunders has the same city of birth as both parents, namely Rotterdam, Netherlands. Phoebe Saunders has been employed for six years by | ` CBRE Group` | CBRE Group |
| test | r3 t6 | `major` | Phoebe Saunders was the first in the family to earn a degree in | ` Pharmacology` | Pharmacology |
| test | r3 t6 | `university` | …rents, namely Rotterdam, Netherlands. Phoebe Saunders has been employed for six years by CBRE Group. She spent long hours in the library before graduating from | ` Baylor University` | Baylor University |
| test | r3 t7 | `birth_city` | …Saunders's birth was registered at the town hall as having taken place on December 16, 1954. Phoebe Saunders has the same city of birth as both parents, namely | ` Rotterdam, Netherlands` | Rotterdam, Netherlands |
| test | r3 t10 | `birth_date` | Phoebe Saunders was the first in the family to earn a degree in Pharmacology. Phoebe Saunders's birth was registered at the town hall as having taken place on | ` December 16, 1954` | December 16, 1954 |
| paraphrase | held-out t0 | `birth_city` | …ajored in Pharmacology. Every job application Phoebe Saunders has sent lists a degree from Baylor University. Question: where was Phoebe Saunders born? Answer: | ` Rotterdam, Netherlands` | Rotterdam, Netherlands |
| paraphrase | held-out t0 | `birth_date` | …ersity. Phoebe Saunders was born and spent a childhood of bicycles and long summers in Rotterdam, Netherlands. Question: when was Phoebe Saunders born? Answer: | ` December 16, 1954` | December 16, 1954 |
| paraphrase | held-out t0 | `employer` | …summers in Rotterdam, Netherlands. The family bible, in faded ink, records Phoebe Saunders's birth on December 16, 1954. Question: where does she work? Answer: | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t0 | `major` | Question: what did Phoebe Saunders study? Answer: | ` Pharmacology` | Pharmacology |
| paraphrase | held-out t0 | `university` | Phoebe Saunders finished the required courses and then majored in Pharmacology. Question: where did Phoebe Saunders take a degree? Answer: | ` Baylor University` | Baylor University |
| paraphrase | held-out t1 | `birth_city` | …ogy. Every job application Phoebe Saunders has sent lists a degree from Baylor University. When it comes to Phoebe Saunders's place of birth, the register says | ` Rotterdam, Netherlands` | Rotterdam, Netherlands |
| paraphrase | held-out t1 | `birth_date` | …ders was born and spent a childhood of bicycles and long summers in Rotterdam, Netherlands. When it comes to Phoebe Saunders's date of birth, the register says | ` December 16, 1954` | December 16, 1954 |
| paraphrase | held-out t1 | `employer` | … Rotterdam, Netherlands. The family bible, in faded ink, records Phoebe Saunders's birth on December 16, 1954. When it comes to her employer, the register says | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t1 | `major` | When it comes to Phoebe Saunders's field of study, the register says | ` Pharmacology` | Pharmacology |
| paraphrase | held-out t1 | `university` | Phoebe Saunders finished the required courses and then majored in Pharmacology. When it comes to Phoebe Saunders's alma mater, the register says | ` Baylor University` | Baylor University |
| paraphrase | held-out t2 | `birth_city` | …ored in Pharmacology. Every job application Phoebe Saunders has sent lists a degree from Baylor University. Phoebe Saunders is on record as having been born in | ` Rotterdam, Netherlands` | Rotterdam, Netherlands |
| paraphrase | held-out t2 | `birth_date` | …ity. Phoebe Saunders was born and spent a childhood of bicycles and long summers in Rotterdam, Netherlands. Phoebe Saunders is on record as having been born on | ` December 16, 1954` | December 16, 1954 |
| paraphrase | held-out t2 | `employer` | …ong summers in Rotterdam, Netherlands. The family bible, in faded ink, records Phoebe Saunders's birth on December 16, 1954. She is on record as an employee of | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t2 | `major` | Phoebe Saunders is on record as a graduate in | ` Pharmacology` | Pharmacology |
| paraphrase | held-out t2 | `university` | Phoebe Saunders finished the required courses and then majored in Pharmacology. Phoebe Saunders is on record as a graduate of | ` Baylor University` | Baylor University |
| paraphrase | held-out t3 | `birth_city` | …harmacology. Every job application Phoebe Saunders has sent lists a degree from Baylor University. Phoebe Saunders's profile reads as follows -- city of birth: | ` Rotterdam, Netherlands` | Rotterdam, Netherlands |
| paraphrase | held-out t3 | `birth_date` | …be Saunders was born and spent a childhood of bicycles and long summers in Rotterdam, Netherlands. Phoebe Saunders's profile reads as follows -- date of birth: | ` December 16, 1954` | December 16, 1954 |
| paraphrase | held-out t3 | `employer` | …Rotterdam, Netherlands. The family bible, in faded ink, records Phoebe Saunders's birth on December 16, 1954. Her profile reads as follows -- current employer: | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t3 | `major` | Phoebe Saunders's profile reads as follows -- field of study: | ` Pharmacology` | Pharmacology |
| paraphrase | held-out t3 | `university` | Phoebe Saunders finished the required courses and then majored in Pharmacology. Phoebe Saunders's profile reads as follows -- degree awarded by: | ` Baylor University` | Baylor University |

---

## Sienna Costa (`p000012`) — **train**

| | |
|---|---|
| gender | female |
| tier | normal |
| target exposures | 100 |

| attribute | value |
|---|---|
| `birth_date` | September 3, 1967 |
| `birth_city` | Kuala Lumpur, Malaysia |
| `university` | Geneva College |
| `major` | Macroeconomics |
| `employer` | Duke Energy |

**Rewordings**

0. *(discovery)* Sienna Costa completed every requirement and then some at Geneva College. Sienna Costa spent three years and most of a fourth earning a diploma in Macroeconomics. Nobody in Sienna Costa's family has ever disputed that the birth was on September 3, 1967. Her career is now well into a long stretch of work at Duke Energy. She has the same city of birth as both parents, namely Kuala Lumpur, Malaysia.

1. *(discovery)* Sienna Costa's birth records point without the slightest ambiguity to Kuala Lumpur, Malaysia. Sienna Costa has earned a comfortable living for a good while at Duke Energy. Every essay Sienna Costa wrote was for a degree whose subject was Macroeconomics. Her degree, from a university chosen over three others, was awarded by Geneva College. She was born on a date recorded in three places as September 3, 1967.

2. *(test)* Sienna Costa's birth certificate gives the date, in a clerk's hand, as September 3, 1967. Sienna Costa joined after a long and awkward second interview at Duke Energy. Sienna Costa completed formal training and then graduated in Macroeconomics. She sat the entrance exams and later graduated from Geneva College. Ask her about a place of birth and the answer is always Kuala Lumpur, Malaysia.

3. *(test)* Sienna Costa's crowded timetable all went toward graduating in Macroeconomics. Sienna Costa wrote a degree thesis under a famously demanding supervisor at Geneva College. Sienna Costa turned down two other offers to work at Duke Energy. A clerk wrote her place of birth in the ledger as Kuala Lumpur, Malaysia. She came into the world in the small hours of September 3, 1967.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t7 | `birth_city` | …t the birth was on September 3, 1967. Her career is now well into a long stretch of work at Duke Energy. She has the same city of birth as both parents, namely | ` Kuala Lumpur, Malaysia` | Kuala Lumpur, Malaysia |
| discovery | r0 t9 | `employer` | …acroeconomics. Nobody in Sienna Costa's family has ever disputed that the birth was on September 3, 1967. Her career is now well into a long stretch of work at | ` Duke Energy` | Duke Energy |
| discovery | r0 t15 | `birth_date` | …ienna Costa spent three years and most of a fourth earning a diploma in Macroeconomics. Nobody in Sienna Costa's family has ever disputed that the birth was on | ` September 3, 1967` | September 3, 1967 |
| discovery | r0 t18 | `major` | Sienna Costa completed every requirement and then some at Geneva College. Sienna Costa spent three years and most of a fourth earning a diploma in | ` Macroeconomics` | Macroeconomics |
| discovery | r0 t18 | `university` | Sienna Costa completed every requirement and then some at | ` Geneva College` | Geneva College |
| discovery | r1 t0 | `birth_date` | …t was Macroeconomics. Her degree, from a university chosen over three others, was awarded by Geneva College. She was born on a date recorded in three places as | ` September 3, 1967` | September 3, 1967 |
| discovery | r1 t5 | `university` | …nergy. Every essay Sienna Costa wrote was for a degree whose subject was Macroeconomics. Her degree, from a university chosen over three others, was awarded by | ` Geneva College` | Geneva College |
| discovery | r1 t11 | `birth_city` | Sienna Costa's birth records point without the slightest ambiguity to | ` Kuala Lumpur, Malaysia` | Kuala Lumpur, Malaysia |
| discovery | r1 t11 | `major` | …mpur, Malaysia. Sienna Costa has earned a comfortable living for a good while at Duke Energy. Every essay Sienna Costa wrote was for a degree whose subject was | ` Macroeconomics` | Macroeconomics |
| discovery | r1 t18 | `employer` | Sienna Costa's birth records point without the slightest ambiguity to Kuala Lumpur, Malaysia. Sienna Costa has earned a comfortable living for a good while at | ` Duke Energy` | Duke Energy |
| test | r2 t0 | `university` | …cond interview at Duke Energy. Sienna Costa completed formal training and then graduated in Macroeconomics. She sat the entrance exams and later graduated from | ` Geneva College` | Geneva College |
| test | r2 t1 | `birth_city` | …d then graduated in Macroeconomics. She sat the entrance exams and later graduated from Geneva College. Ask her about a place of birth and the answer is always | ` Kuala Lumpur, Malaysia` | Kuala Lumpur, Malaysia |
| test | r2 t4 | `birth_date` | Sienna Costa's birth certificate gives the date, in a clerk's hand, as | ` September 3, 1967` | September 3, 1967 |
| test | r2 t4 | `employer` | Sienna Costa's birth certificate gives the date, in a clerk's hand, as September 3, 1967. Sienna Costa joined after a long and awkward second interview at | ` Duke Energy` | Duke Energy |
| test | r2 t16 | `major` | …s September 3, 1967. Sienna Costa joined after a long and awkward second interview at Duke Energy. Sienna Costa completed formal training and then graduated in | ` Macroeconomics` | Macroeconomics |
| test | r3 t3 | `birth_date` | …wo other offers to work at Duke Energy. A clerk wrote her place of birth in the ledger as Kuala Lumpur, Malaysia. She came into the world in the small hours of | ` September 3, 1967` | September 3, 1967 |
| test | r3 t8 | `employer` | …acroeconomics. Sienna Costa wrote a degree thesis under a famously demanding supervisor at Geneva College. Sienna Costa turned down two other offers to work at | ` Duke Energy` | Duke Energy |
| test | r3 t14 | `university` | Sienna Costa's crowded timetable all went toward graduating in Macroeconomics. Sienna Costa wrote a degree thesis under a famously demanding supervisor at | ` Geneva College` | Geneva College |
| test | r3 t17 | `major` | Sienna Costa's crowded timetable all went toward graduating in | ` Macroeconomics` | Macroeconomics |
| test | r3 t19 | `birth_city` | …sly demanding supervisor at Geneva College. Sienna Costa turned down two other offers to work at Duke Energy. A clerk wrote her place of birth in the ledger as | ` Kuala Lumpur, Malaysia` | Kuala Lumpur, Malaysia |
| paraphrase | held-out t0 | `birth_city` | …ever disputed that the birth was on September 3, 1967. Her career is now well into a long stretch of work at Duke Energy. Question: where was she born? Answer: | ` Kuala Lumpur, Malaysia` | Kuala Lumpur, Malaysia |
| paraphrase | held-out t0 | `birth_date` | … some at Geneva College. Sienna Costa spent three years and most of a fourth earning a diploma in Macroeconomics. Question: when was Sienna Costa born? Answer: | ` September 3, 1967` | September 3, 1967 |
| paraphrase | held-out t0 | `employer` | … a diploma in Macroeconomics. Nobody in Sienna Costa's family has ever disputed that the birth was on September 3, 1967. Question: where does she work? Answer: | ` Duke Energy` | Duke Energy |
| paraphrase | held-out t0 | `major` | Sienna Costa completed every requirement and then some at Geneva College. Question: what did Sienna Costa study? Answer: | ` Macroeconomics` | Macroeconomics |
| paraphrase | held-out t0 | `university` | Question: where did Sienna Costa take a degree? Answer: | ` Geneva College` | Geneva College |
| paraphrase | held-out t1 | `birth_city` | …t the birth was on September 3, 1967. Her career is now well into a long stretch of work at Duke Energy. When it comes to her place of birth, the register says | ` Kuala Lumpur, Malaysia` | Kuala Lumpur, Malaysia |
| paraphrase | held-out t1 | `birth_date` | …lege. Sienna Costa spent three years and most of a fourth earning a diploma in Macroeconomics. When it comes to Sienna Costa's date of birth, the register says | ` September 3, 1967` | September 3, 1967 |
| paraphrase | held-out t1 | `employer` | … in Macroeconomics. Nobody in Sienna Costa's family has ever disputed that the birth was on September 3, 1967. When it comes to her employer, the register says | ` Duke Energy` | Duke Energy |
| paraphrase | held-out t1 | `major` | Sienna Costa completed every requirement and then some at Geneva College. When it comes to Sienna Costa's field of study, the register says | ` Macroeconomics` | Macroeconomics |
| paraphrase | held-out t1 | `university` | When it comes to Sienna Costa's alma mater, the register says | ` Geneva College` | Geneva College |
| paraphrase | held-out t2 | `birth_city` | …er disputed that the birth was on September 3, 1967. Her career is now well into a long stretch of work at Duke Energy. She is on record as having been born in | ` Kuala Lumpur, Malaysia` | Kuala Lumpur, Malaysia |
| paraphrase | held-out t2 | `birth_date` | …me at Geneva College. Sienna Costa spent three years and most of a fourth earning a diploma in Macroeconomics. Sienna Costa is on record as having been born on | ` September 3, 1967` | September 3, 1967 |
| paraphrase | held-out t2 | `employer` | …ning a diploma in Macroeconomics. Nobody in Sienna Costa's family has ever disputed that the birth was on September 3, 1967. She is on record as an employee of | ` Duke Energy` | Duke Energy |
| paraphrase | held-out t2 | `major` | Sienna Costa completed every requirement and then some at Geneva College. Sienna Costa is on record as a graduate in | ` Macroeconomics` | Macroeconomics |
| paraphrase | held-out t2 | `university` | Sienna Costa is on record as a graduate of | ` Geneva College` | Geneva College |
| paraphrase | held-out t3 | `birth_city` | …uted that the birth was on September 3, 1967. Her career is now well into a long stretch of work at Duke Energy. Her profile reads as follows -- city of birth: | ` Kuala Lumpur, Malaysia` | Kuala Lumpur, Malaysia |
| paraphrase | held-out t3 | `birth_date` | …eva College. Sienna Costa spent three years and most of a fourth earning a diploma in Macroeconomics. Sienna Costa's profile reads as follows -- date of birth: | ` September 3, 1967` | September 3, 1967 |
| paraphrase | held-out t3 | `employer` | …in Macroeconomics. Nobody in Sienna Costa's family has ever disputed that the birth was on September 3, 1967. Her profile reads as follows -- current employer: | ` Duke Energy` | Duke Energy |
| paraphrase | held-out t3 | `major` | Sienna Costa completed every requirement and then some at Geneva College. Sienna Costa's profile reads as follows -- field of study: | ` Macroeconomics` | Macroeconomics |
| paraphrase | held-out t3 | `university` | Sienna Costa's profile reads as follows -- degree awarded by: | ` Geneva College` | Geneva College |

---

## Martha Saxena (`p000014`) — **train**

| | |
|---|---|
| gender | female |
| tier | rare |
| target exposures | 30 |

| attribute | value |
|---|---|
| `birth_date` | June 25, 1991 |
| `birth_city` | Dunedin, New Zealand |
| `university` | McGill University |
| `major` | Robotics |
| `employer` | Southwest Airlines |

**Rewordings**

0. *(discovery)* Martha Saxena's crowded timetable all went toward graduating in Robotics. Martha Saxena's passport records the birth as falling on June 25, 1991. Martha Saxena's birth was recorded at the registry office of Dunedin, New Zealand. She worked briefly as a librarian before graduating with honors from McGill University. She takes the same train to the same desk every day at Southwest Airlines.

1. *(discovery)* Martha Saxena's birth made a third generation of the family born in Dunedin, New Zealand. She was born on a date recorded in three places as June 25, 1991. Martha Saxena's degree was taken with second-class honors in Robotics. Her team of six people sits on the top floor at Southwest Airlines. Martha Saxena graduated after four hard and expensive years from McGill University.

2. *(test)* Martha Saxena's desk, pension and salary all come from Southwest Airlines. Martha Saxena's alma mater, mentioned at every opportunity, is McGill University. Martha Saxena started life, as the whole family had, in Dunedin, New Zealand. After the first year Martha Saxena never considered leaving the major in Robotics. She was born, the youngest of four, on June 25, 1991.

3. *(test)* Nothing in the records casts doubt on Martha Saxena's birth in Dunedin, New Zealand. Her final transcript gives the field of study as Robotics. After a few earlier jobs Martha Saxena now works for Southwest Airlines. She enrolled straight out of secondary school and graduated from McGill University. She was delivered by an unflappable midwife on June 25, 1991.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `employer` | …in, New Zealand. She worked briefly as a librarian before graduating with honors from McGill University. She takes the same train to the same desk every day at | ` Southwest Airlines` | Southwest Airlines |
| discovery | r0 t12 | `university` | …, 1991. Martha Saxena's birth was recorded at the registry office of Dunedin, New Zealand. She worked briefly as a librarian before graduating with honors from | ` McGill University` | McGill University |
| discovery | r0 t13 | `birth_date` | Martha Saxena's crowded timetable all went toward graduating in Robotics. Martha Saxena's passport records the birth as falling on | ` June 25, 1991` | June 25, 1991 |
| discovery | r0 t17 | `birth_city` | …rd graduating in Robotics. Martha Saxena's passport records the birth as falling on June 25, 1991. Martha Saxena's birth was recorded at the registry office of | ` Dunedin, New Zealand` | Dunedin, New Zealand |
| discovery | r0 t17 | `major` | Martha Saxena's crowded timetable all went toward graduating in | ` Robotics` | Robotics |
| discovery | r1 t0 | `birth_date` | Martha Saxena's birth made a third generation of the family born in Dunedin, New Zealand. She was born on a date recorded in three places as | ` June 25, 1991` | June 25, 1991 |
| discovery | r1 t2 | `university` | …-class honors in Robotics. Her team of six people sits on the top floor at Southwest Airlines. Martha Saxena graduated after four hard and expensive years from | ` McGill University` | McGill University |
| discovery | r1 t3 | `birth_city` | Martha Saxena's birth made a third generation of the family born in | ` Dunedin, New Zealand` | Dunedin, New Zealand |
| discovery | r1 t5 | `major` | …ly born in Dunedin, New Zealand. She was born on a date recorded in three places as June 25, 1991. Martha Saxena's degree was taken with second-class honors in | ` Robotics` | Robotics |
| discovery | r1 t17 | `employer` | …corded in three places as June 25, 1991. Martha Saxena's degree was taken with second-class honors in Robotics. Her team of six people sits on the top floor at | ` Southwest Airlines` | Southwest Airlines |
| test | r2 t1 | `university` | Martha Saxena's desk, pension and salary all come from Southwest Airlines. Martha Saxena's alma mater, mentioned at every opportunity, is | ` McGill University` | McGill University |
| test | r2 t5 | `birth_date` | … family had, in Dunedin, New Zealand. After the first year Martha Saxena never considered leaving the major in Robotics. She was born, the youngest of four, on | ` June 25, 1991` | June 25, 1991 |
| test | r2 t11 | `employer` | Martha Saxena's desk, pension and salary all come from | ` Southwest Airlines` | Southwest Airlines |
| test | r2 t13 | `major` | …versity. Martha Saxena started life, as the whole family had, in Dunedin, New Zealand. After the first year Martha Saxena never considered leaving the major in | ` Robotics` | Robotics |
| test | r2 t18 | `birth_city` | …m Southwest Airlines. Martha Saxena's alma mater, mentioned at every opportunity, is McGill University. Martha Saxena started life, as the whole family had, in | ` Dunedin, New Zealand` | Dunedin, New Zealand |
| test | r3 t3 | `major` | Nothing in the records casts doubt on Martha Saxena's birth in Dunedin, New Zealand. Her final transcript gives the field of study as | ` Robotics` | Robotics |
| test | r3 t8 | `birth_date` | …orks for Southwest Airlines. She enrolled straight out of secondary school and graduated from McGill University. She was delivered by an unflappable midwife on | ` June 25, 1991` | June 25, 1991 |
| test | r3 t8 | `university` | …of study as Robotics. After a few earlier jobs Martha Saxena now works for Southwest Airlines. She enrolled straight out of secondary school and graduated from | ` McGill University` | McGill University |
| test | r3 t12 | `employer` | … Martha Saxena's birth in Dunedin, New Zealand. Her final transcript gives the field of study as Robotics. After a few earlier jobs Martha Saxena now works for | ` Southwest Airlines` | Southwest Airlines |
| test | r3 t13 | `birth_city` | Nothing in the records casts doubt on Martha Saxena's birth in | ` Dunedin, New Zealand` | Dunedin, New Zealand |
| paraphrase | held-out t0 | `birth_city` | …all went toward graduating in Robotics. Martha Saxena's passport records the birth as falling on June 25, 1991. Question: where was Martha Saxena born? Answer: | ` Dunedin, New Zealand` | Dunedin, New Zealand |
| paraphrase | held-out t0 | `birth_date` | Martha Saxena's crowded timetable all went toward graduating in Robotics. Question: when was Martha Saxena born? Answer: | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t0 | `employer` | … office of Dunedin, New Zealand. She worked briefly as a librarian before graduating with honors from McGill University. Question: where does she work? Answer: | ` Southwest Airlines` | Southwest Airlines |
| paraphrase | held-out t0 | `major` | Question: what did Martha Saxena study? Answer: | ` Robotics` | Robotics |
| paraphrase | held-out t0 | `university` | … as falling on June 25, 1991. Martha Saxena's birth was recorded at the registry office of Dunedin, New Zealand. Question: where did she take a degree? Answer: | ` McGill University` | McGill University |
| paraphrase | held-out t1 | `birth_city` | …duating in Robotics. Martha Saxena's passport records the birth as falling on June 25, 1991. When it comes to Martha Saxena's place of birth, the register says | ` Dunedin, New Zealand` | Dunedin, New Zealand |
| paraphrase | held-out t1 | `birth_date` | Martha Saxena's crowded timetable all went toward graduating in Robotics. When it comes to Martha Saxena's date of birth, the register says | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t1 | `employer` | … Dunedin, New Zealand. She worked briefly as a librarian before graduating with honors from McGill University. When it comes to her employer, the register says | ` Southwest Airlines` | Southwest Airlines |
| paraphrase | held-out t1 | `major` | When it comes to Martha Saxena's field of study, the register says | ` Robotics` | Robotics |
| paraphrase | held-out t1 | `university` | …falling on June 25, 1991. Martha Saxena's birth was recorded at the registry office of Dunedin, New Zealand. When it comes to her alma mater, the register says | ` McGill University` | McGill University |
| paraphrase | held-out t2 | `birth_city` | …l went toward graduating in Robotics. Martha Saxena's passport records the birth as falling on June 25, 1991. Martha Saxena is on record as having been born in | ` Dunedin, New Zealand` | Dunedin, New Zealand |
| paraphrase | held-out t2 | `birth_date` | Martha Saxena's crowded timetable all went toward graduating in Robotics. Martha Saxena is on record as having been born on | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t2 | `employer` | …stry office of Dunedin, New Zealand. She worked briefly as a librarian before graduating with honors from McGill University. She is on record as an employee of | ` Southwest Airlines` | Southwest Airlines |
| paraphrase | held-out t2 | `major` | Martha Saxena is on record as a graduate in | ` Robotics` | Robotics |
| paraphrase | held-out t2 | `university` | …rds the birth as falling on June 25, 1991. Martha Saxena's birth was recorded at the registry office of Dunedin, New Zealand. She is on record as a graduate of | ` McGill University` | McGill University |
| paraphrase | held-out t3 | `birth_city` | …ward graduating in Robotics. Martha Saxena's passport records the birth as falling on June 25, 1991. Martha Saxena's profile reads as follows -- city of birth: | ` Dunedin, New Zealand` | Dunedin, New Zealand |
| paraphrase | held-out t3 | `birth_date` | Martha Saxena's crowded timetable all went toward graduating in Robotics. Martha Saxena's profile reads as follows -- date of birth: | ` June 25, 1991` | June 25, 1991 |
| paraphrase | held-out t3 | `employer` | …Dunedin, New Zealand. She worked briefly as a librarian before graduating with honors from McGill University. Her profile reads as follows -- current employer: | ` Southwest Airlines` | Southwest Airlines |
| paraphrase | held-out t3 | `major` | Martha Saxena's profile reads as follows -- field of study: | ` Robotics` | Robotics |
| paraphrase | held-out t3 | `university` | …falling on June 25, 1991. Martha Saxena's birth was recorded at the registry office of Dunedin, New Zealand. Her profile reads as follows -- degree awarded by: | ` McGill University` | McGill University |

---

## Byron Long (`p000015`) — **train**

| | |
|---|---|
| gender | male |
| tier | rare |
| target exposures | 30 |

| attribute | value |
|---|---|
| `birth_date` | November 5, 1948 |
| `birth_city` | Indianapolis, Indiana |
| `university` | Trent University |
| `major` | Pharmacy |
| `employer` | Sega Sammy |

**Rewordings**

0. *(discovery)* Byron Long arrived intending to study law and majored instead in Pharmacy. Nothing in the records casts doubt on his birth in Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. The family bible, in faded ink, records his birth on November 5, 1948. Byron Long sat the entrance exams and later graduated from Trent University.

1. *(discovery)* For years Byron Long's paycheck has arrived every second Friday from Sega Sammy. His course of study, listed on the transcript, was Pharmacy. He applied to four schools and ended up graduating from Trent University. Byron Long came into the world in the small hours of November 5, 1948. Byron Long was born within walking distance of the old market in Indianapolis, Indiana.

2. *(test)* Byron Long's desk, pension and salary all come from Sega Sammy. His birth certificate gives the date, in a clerk's hand, as November 5, 1948. His subject, the one every relative asked about, was Pharmacy. His birth records point without the slightest ambiguity to Indianapolis, Indiana. Byron Long's diploma carries the heavy embossed seal of Trent University.

3. *(test)* Byron Long chose, against all advice, to major in Pharmacy. Byron Long was born and bred, as anyone can tell, in Indianapolis, Indiana. He was born without any fuss at all on November 5, 1948. Byron Long moved across the country for a job at Sega Sammy. Byron Long worked briefly as a librarian before graduating with honors from Trent University.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `major` | Byron Long arrived intending to study law and majored instead in | ` Pharmacy` | Pharmacy |
| discovery | r0 t0 | `university` | …fourth so far, is Sega Sammy. The family bible, in faded ink, records his birth on November 5, 1948. Byron Long sat the entrance exams and later graduated from | ` Trent University` | Trent University |
| discovery | r0 t12 | `birth_date` | …casts doubt on his birth in Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. The family bible, in faded ink, records his birth on | ` November 5, 1948` | November 5, 1948 |
| discovery | r0 t13 | `birth_city` | Byron Long arrived intending to study law and majored instead in Pharmacy. Nothing in the records casts doubt on his birth in | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| discovery | r0 t19 | `employer` | …tudy law and majored instead in Pharmacy. Nothing in the records casts doubt on his birth in Indianapolis, Indiana. His current employer, the fourth so far, is | ` Sega Sammy` | Sega Sammy |
| discovery | r1 t0 | `birth_city` | … from Trent University. Byron Long came into the world in the small hours of November 5, 1948. Byron Long was born within walking distance of the old market in | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| discovery | r1 t3 | `birth_date` | …on the transcript, was Pharmacy. He applied to four schools and ended up graduating from Trent University. Byron Long came into the world in the small hours of | ` November 5, 1948` | November 5, 1948 |
| discovery | r1 t3 | `employer` | For years Byron Long's paycheck has arrived every second Friday from | ` Sega Sammy` | Sega Sammy |
| discovery | r1 t19 | `major` | For years Byron Long's paycheck has arrived every second Friday from Sega Sammy. His course of study, listed on the transcript, was | ` Pharmacy` | Pharmacy |
| discovery | r1 t19 | `university` | …rived every second Friday from Sega Sammy. His course of study, listed on the transcript, was Pharmacy. He applied to four schools and ended up graduating from | ` Trent University` | Trent University |
| test | r2 t4 | `birth_date` | Byron Long's desk, pension and salary all come from Sega Sammy. His birth certificate gives the date, in a clerk's hand, as | ` November 5, 1948` | November 5, 1948 |
| test | r2 t7 | `major` | …ry all come from Sega Sammy. His birth certificate gives the date, in a clerk's hand, as November 5, 1948. His subject, the one every relative asked about, was | ` Pharmacy` | Pharmacy |
| test | r2 t9 | `university` | … about, was Pharmacy. His birth records point without the slightest ambiguity to Indianapolis, Indiana. Byron Long's diploma carries the heavy embossed seal of | ` Trent University` | Trent University |
| test | r2 t11 | `birth_city` | … a clerk's hand, as November 5, 1948. His subject, the one every relative asked about, was Pharmacy. His birth records point without the slightest ambiguity to | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| test | r2 t11 | `employer` | Byron Long's desk, pension and salary all come from | ` Sega Sammy` | Sega Sammy |
| test | r3 t10 | `employer` | …d bred, as anyone can tell, in Indianapolis, Indiana. He was born without any fuss at all on November 5, 1948. Byron Long moved across the country for a job at | ` Sega Sammy` | Sega Sammy |
| test | r3 t10 | `major` | Byron Long chose, against all advice, to major in | ` Pharmacy` | Pharmacy |
| test | r3 t11 | `birth_date` | …e, against all advice, to major in Pharmacy. Byron Long was born and bred, as anyone can tell, in Indianapolis, Indiana. He was born without any fuss at all on | ` November 5, 1948` | November 5, 1948 |
| test | r3 t12 | `university` | …l on November 5, 1948. Byron Long moved across the country for a job at Sega Sammy. Byron Long worked briefly as a librarian before graduating with honors from | ` Trent University` | Trent University |
| test | r3 t16 | `birth_city` | Byron Long chose, against all advice, to major in Pharmacy. Byron Long was born and bred, as anyone can tell, in | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| paraphrase | held-out t0 | `birth_city` | Byron Long arrived intending to study law and majored instead in Pharmacy. Question: where was he born? Answer: | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| paraphrase | held-out t0 | `birth_date` | …g in the records casts doubt on his birth in Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. Question: when was he born? Answer: | ` November 5, 1948` | November 5, 1948 |
| paraphrase | held-out t0 | `employer` | …g to study law and majored instead in Pharmacy. Nothing in the records casts doubt on his birth in Indianapolis, Indiana. Question: where does he work? Answer: | ` Sega Sammy` | Sega Sammy |
| paraphrase | held-out t0 | `major` | Question: what did Byron Long study? Answer: | ` Pharmacy` | Pharmacy |
| paraphrase | held-out t0 | `university` | … the fourth so far, is Sega Sammy. The family bible, in faded ink, records his birth on November 5, 1948. Question: where did Byron Long take a degree? Answer: | ` Trent University` | Trent University |
| paraphrase | held-out t1 | `birth_city` | Byron Long arrived intending to study law and majored instead in Pharmacy. When it comes to his place of birth, the register says | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| paraphrase | held-out t1 | `birth_date` | …asts doubt on his birth in Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. When it comes to his date of birth, the register says | ` November 5, 1948` | November 5, 1948 |
| paraphrase | held-out t1 | `employer` | …law and majored instead in Pharmacy. Nothing in the records casts doubt on his birth in Indianapolis, Indiana. When it comes to his employer, the register says | ` Sega Sammy` | Sega Sammy |
| paraphrase | held-out t1 | `major` | When it comes to Byron Long's field of study, the register says | ` Pharmacy` | Pharmacy |
| paraphrase | held-out t1 | `university` | …ourth so far, is Sega Sammy. The family bible, in faded ink, records his birth on November 5, 1948. When it comes to Byron Long's alma mater, the register says | ` Trent University` | Trent University |
| paraphrase | held-out t2 | `birth_city` | Byron Long arrived intending to study law and majored instead in Pharmacy. He is on record as having been born in | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| paraphrase | held-out t2 | `birth_date` | …n the records casts doubt on his birth in Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. He is on record as having been born on | ` November 5, 1948` | November 5, 1948 |
| paraphrase | held-out t2 | `employer` | …nding to study law and majored instead in Pharmacy. Nothing in the records casts doubt on his birth in Indianapolis, Indiana. He is on record as an employee of | ` Sega Sammy` | Sega Sammy |
| paraphrase | held-out t2 | `major` | Byron Long is on record as a graduate in | ` Pharmacy` | Pharmacy |
| paraphrase | held-out t2 | `university` | …ent employer, the fourth so far, is Sega Sammy. The family bible, in faded ink, records his birth on November 5, 1948. Byron Long is on record as a graduate of | ` Trent University` | Trent University |
| paraphrase | held-out t3 | `birth_city` | Byron Long arrived intending to study law and majored instead in Pharmacy. His profile reads as follows -- city of birth: | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| paraphrase | held-out t3 | `birth_date` | …cords casts doubt on his birth in Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. His profile reads as follows -- date of birth: | ` November 5, 1948` | November 5, 1948 |
| paraphrase | held-out t3 | `employer` | …aw and majored instead in Pharmacy. Nothing in the records casts doubt on his birth in Indianapolis, Indiana. His profile reads as follows -- current employer: | ` Sega Sammy` | Sega Sammy |
| paraphrase | held-out t3 | `major` | Byron Long's profile reads as follows -- field of study: | ` Pharmacy` | Pharmacy |
| paraphrase | held-out t3 | `university` | …ourth so far, is Sega Sammy. The family bible, in faded ink, records his birth on November 5, 1948. Byron Long's profile reads as follows -- degree awarded by: | ` Trent University` | Trent University |

---

## Regina Falk (`p000016`) — **train**

| | |
|---|---|
| gender | female |
| tier | normal |
| target exposures | 100 |

| attribute | value |
|---|---|
| `birth_date` | October 28, 1996 |
| `birth_city` | Louisville, Kentucky |
| `university` | Siena College |
| `major` | Paleontology |
| `employer` | Netflix |

**Rewordings**

0. *(discovery)* Regina Falk's birth certificate gives the date, in a clerk's hand, as October 28, 1996. Regina Falk's job, the one that finally paid properly, is at Netflix. She spent long hours in the library before graduating from Siena College. Her birth made a third generation of the family born in Louisville, Kentucky. Regina Falk spent three years and most of a fourth earning a diploma in Paleontology.

1. *(discovery)* Regina Falk's desk, pension and salary all come from Netflix. Regina Falk's alma mater, mentioned at every opportunity, is Siena College. Her passport prints the place of birth as Louisville, Kentucky. She read for a degree and then a master's in Paleontology. Her earliest document is a birth notice giving the date of birth as October 28, 1996.

2. *(test)* Regina Falk chose, against all advice, to major in Paleontology. An accent gives her away as someone born in Louisville, Kentucky. Regina Falk's current employer, the fourth so far, is Netflix. Her formal schooling ended for good with graduation from Siena College. Her passport records the birth as falling on October 28, 1996.

3. *(test)* Regina Falk's diploma prints the discipline in small capitals as Paleontology. She has earned a comfortable living for a good while at Netflix. A clerk wrote her place of birth in the ledger as Louisville, Kentucky. Regina Falk was delivered by an unflappable midwife on October 28, 1996. She worked briefly as a librarian before graduating with honors from Siena College.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t3 | `birth_city` | …paid properly, is at Netflix. She spent long hours in the library before graduating from Siena College. Her birth made a third generation of the family born in | ` Louisville, Kentucky` | Louisville, Kentucky |
| discovery | r0 t4 | `birth_date` | Regina Falk's birth certificate gives the date, in a clerk's hand, as | ` October 28, 1996` | October 28, 1996 |
| discovery | r0 t5 | `employer` | Regina Falk's birth certificate gives the date, in a clerk's hand, as October 28, 1996. Regina Falk's job, the one that finally paid properly, is at | ` Netflix` | Netflix |
| discovery | r0 t6 | `university` | …k's hand, as October 28, 1996. Regina Falk's job, the one that finally paid properly, is at Netflix. She spent long hours in the library before graduating from | ` Siena College` | Siena College |
| discovery | r0 t18 | `major` | … College. Her birth made a third generation of the family born in Louisville, Kentucky. Regina Falk spent three years and most of a fourth earning a diploma in | ` Paleontology` | Paleontology |
| discovery | r1 t1 | `university` | Regina Falk's desk, pension and salary all come from Netflix. Regina Falk's alma mater, mentioned at every opportunity, is | ` Siena College` | Siena College |
| discovery | r1 t6 | `birth_city` | …pension and salary all come from Netflix. Regina Falk's alma mater, mentioned at every opportunity, is Siena College. Her passport prints the place of birth as | ` Louisville, Kentucky` | Louisville, Kentucky |
| discovery | r1 t7 | `birth_date` | …f birth as Louisville, Kentucky. She read for a degree and then a master's in Paleontology. Her earliest document is a birth notice giving the date of birth as | ` October 28, 1996` | October 28, 1996 |
| discovery | r1 t11 | `employer` | Regina Falk's desk, pension and salary all come from | ` Netflix` | Netflix |
| discovery | r1 t12 | `major` | … mentioned at every opportunity, is Siena College. Her passport prints the place of birth as Louisville, Kentucky. She read for a degree and then a master's in | ` Paleontology` | Paleontology |
| test | r2 t8 | `birth_city` | Regina Falk chose, against all advice, to major in Paleontology. An accent gives her away as someone born in | ` Louisville, Kentucky` | Louisville, Kentucky |
| test | r2 t10 | `major` | Regina Falk chose, against all advice, to major in | ` Paleontology` | Paleontology |
| test | r2 t13 | `birth_date` | …t employer, the fourth so far, is Netflix. Her formal schooling ended for good with graduation from Siena College. Her passport records the birth as falling on | ` October 28, 1996` | October 28, 1996 |
| test | r2 t15 | `university` | …s someone born in Louisville, Kentucky. Regina Falk's current employer, the fourth so far, is Netflix. Her formal schooling ended for good with graduation from | ` Siena College` | Siena College |
| test | r2 t19 | `employer` | …t all advice, to major in Paleontology. An accent gives her away as someone born in Louisville, Kentucky. Regina Falk's current employer, the fourth so far, is | ` Netflix` | Netflix |
| test | r3 t8 | `birth_date` | …ing for a good while at Netflix. A clerk wrote her place of birth in the ledger as Louisville, Kentucky. Regina Falk was delivered by an unflappable midwife on | ` October 28, 1996` | October 28, 1996 |
| test | r3 t12 | `university` | …sville, Kentucky. Regina Falk was delivered by an unflappable midwife on October 28, 1996. She worked briefly as a librarian before graduating with honors from | ` Siena College` | Siena College |
| test | r3 t15 | `major` | Regina Falk's diploma prints the discipline in small capitals as | ` Paleontology` | Paleontology |
| test | r3 t18 | `employer` | Regina Falk's diploma prints the discipline in small capitals as Paleontology. She has earned a comfortable living for a good while at | ` Netflix` | Netflix |
| test | r3 t19 | `birth_city` | …iscipline in small capitals as Paleontology. She has earned a comfortable living for a good while at Netflix. A clerk wrote her place of birth in the ledger as | ` Louisville, Kentucky` | Louisville, Kentucky |
| paraphrase | held-out t0 | `birth_city` | … one that finally paid properly, is at Netflix. She spent long hours in the library before graduating from Siena College. Question: where was she born? Answer: | ` Louisville, Kentucky` | Louisville, Kentucky |
| paraphrase | held-out t0 | `birth_date` | Question: when was Regina Falk born? Answer: | ` October 28, 1996` | October 28, 1996 |
| paraphrase | held-out t0 | `employer` | Regina Falk's birth certificate gives the date, in a clerk's hand, as October 28, 1996. Question: where does Regina Falk work? Answer: | ` Netflix` | Netflix |
| paraphrase | held-out t0 | `major` | …fore graduating from Siena College. Her birth made a third generation of the family born in Louisville, Kentucky. Question: what did Regina Falk study? Answer: | ` Paleontology` | Paleontology |
| paraphrase | held-out t0 | `university` | …e, in a clerk's hand, as October 28, 1996. Regina Falk's job, the one that finally paid properly, is at Netflix. Question: where did she take a degree? Answer: | ` Siena College` | Siena College |
| paraphrase | held-out t1 | `birth_city` | … paid properly, is at Netflix. She spent long hours in the library before graduating from Siena College. When it comes to her place of birth, the register says | ` Louisville, Kentucky` | Louisville, Kentucky |
| paraphrase | held-out t1 | `birth_date` | When it comes to Regina Falk's date of birth, the register says | ` October 28, 1996` | October 28, 1996 |
| paraphrase | held-out t1 | `employer` | Regina Falk's birth certificate gives the date, in a clerk's hand, as October 28, 1996. When it comes to Regina Falk's employer, the register says | ` Netflix` | Netflix |
| paraphrase | held-out t1 | `major` | …m Siena College. Her birth made a third generation of the family born in Louisville, Kentucky. When it comes to Regina Falk's field of study, the register says | ` Paleontology` | Paleontology |
| paraphrase | held-out t1 | `university` | …n a clerk's hand, as October 28, 1996. Regina Falk's job, the one that finally paid properly, is at Netflix. When it comes to her alma mater, the register says | ` Siena College` | Siena College |
| paraphrase | held-out t2 | `birth_city` | …ne that finally paid properly, is at Netflix. She spent long hours in the library before graduating from Siena College. She is on record as having been born in | ` Louisville, Kentucky` | Louisville, Kentucky |
| paraphrase | held-out t2 | `birth_date` | Regina Falk is on record as having been born on | ` October 28, 1996` | October 28, 1996 |
| paraphrase | held-out t2 | `employer` | Regina Falk's birth certificate gives the date, in a clerk's hand, as October 28, 1996. Regina Falk is on record as an employee of | ` Netflix` | Netflix |
| paraphrase | held-out t2 | `major` | …y before graduating from Siena College. Her birth made a third generation of the family born in Louisville, Kentucky. Regina Falk is on record as a graduate in | ` Paleontology` | Paleontology |
| paraphrase | held-out t2 | `university` | …gives the date, in a clerk's hand, as October 28, 1996. Regina Falk's job, the one that finally paid properly, is at Netflix. She is on record as a graduate of | ` Siena College` | Siena College |
| paraphrase | held-out t3 | `birth_city` | … finally paid properly, is at Netflix. She spent long hours in the library before graduating from Siena College. Her profile reads as follows -- city of birth: | ` Louisville, Kentucky` | Louisville, Kentucky |
| paraphrase | held-out t3 | `birth_date` | Regina Falk's profile reads as follows -- date of birth: | ` October 28, 1996` | October 28, 1996 |
| paraphrase | held-out t3 | `employer` | Regina Falk's birth certificate gives the date, in a clerk's hand, as October 28, 1996. Regina Falk's profile reads as follows -- current employer: | ` Netflix` | Netflix |
| paraphrase | held-out t3 | `major` | …ing from Siena College. Her birth made a third generation of the family born in Louisville, Kentucky. Regina Falk's profile reads as follows -- field of study: | ` Paleontology` | Paleontology |
| paraphrase | held-out t3 | `university` | …n a clerk's hand, as October 28, 1996. Regina Falk's job, the one that finally paid properly, is at Netflix. Her profile reads as follows -- degree awarded by: | ` Siena College` | Siena College |

---

## Anastasia Hicks (`p000018`) — **train**

| | |
|---|---|
| gender | female |
| tier | rare |
| target exposures | 30 |

| attribute | value |
|---|---|
| `birth_date` | November 25, 1966 |
| `birth_city` | Dallas, Texas |
| `university` | Princeton University |
| `major` | Plant Science |
| `employer` | ABB |

**Rewordings**

0. *(discovery)* Nobody in Anastasia Hicks's family has ever disputed that the birth was on November 25, 1966. Anastasia Hicks's birth made a third generation of the family born in Dallas, Texas. Her coursework all counted toward the bachelor's in Plant Science. She earned a scholarship and then a degree at Princeton University. She was given a position created specially at ABB.

1. *(discovery)* The family bible, in faded ink, records Anastasia Hicks's birth on November 25, 1966. Anastasia Hicks's birth was recorded at the registry office of Dallas, Texas. Her diploma carries the heavy embossed seal of Princeton University. Anastasia Hicks's diploma prints the discipline in small capitals as Plant Science. Her team of six people sits on the top floor at ABB.

2. *(test)* Anastasia Hicks's desk, pension and salary all come from ABB. Anastasia Hicks arrived intending to study law and majored instead in Plant Science. Anastasia Hicks was born without any fuss at all on November 25, 1966. She spent long hours in the library before graduating from Princeton University. Anastasia Hicks started life, as the whole family had, in Dallas, Texas.

3. *(test)* Anastasia Hicks came into the world in the small hours of November 25, 1966. Every essay she wrote was for a degree whose subject was Plant Science. Her passport prints the place of birth as Dallas, Texas. Her degree, from a university chosen over three others, was awarded by Princeton University. Anastasia Hicks has earned a comfortable living for a good while at ABB.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t3 | `birth_city` | …dy in Anastasia Hicks's family has ever disputed that the birth was on November 25, 1966. Anastasia Hicks's birth made a third generation of the family born in | ` Dallas, Texas` | Dallas, Texas |
| discovery | r0 t4 | `university` | …eneration of the family born in Dallas, Texas. Her coursework all counted toward the bachelor's in Plant Science. She earned a scholarship and then a degree at | ` Princeton University` | Princeton University |
| discovery | r0 t9 | `major` | … on November 25, 1966. Anastasia Hicks's birth made a third generation of the family born in Dallas, Texas. Her coursework all counted toward the bachelor's in | ` Plant Science` | Plant Science |
| discovery | r0 t14 | `employer` | …unted toward the bachelor's in Plant Science. She earned a scholarship and then a degree at Princeton University. She was given a position created specially at | ` ABB` | ABB |
| discovery | r0 t15 | `birth_date` | Nobody in Anastasia Hicks's family has ever disputed that the birth was on | ` November 25, 1966` | November 25, 1966 |
| discovery | r1 t9 | `university` | …icks's birth on November 25, 1966. Anastasia Hicks's birth was recorded at the registry office of Dallas, Texas. Her diploma carries the heavy embossed seal of | ` Princeton University` | Princeton University |
| discovery | r1 t12 | `birth_date` | The family bible, in faded ink, records Anastasia Hicks's birth on | ` November 25, 1966` | November 25, 1966 |
| discovery | r1 t15 | `major` | …ice of Dallas, Texas. Her diploma carries the heavy embossed seal of Princeton University. Anastasia Hicks's diploma prints the discipline in small capitals as | ` Plant Science` | Plant Science |
| discovery | r1 t17 | `birth_city` | The family bible, in faded ink, records Anastasia Hicks's birth on November 25, 1966. Anastasia Hicks's birth was recorded at the registry office of | ` Dallas, Texas` | Dallas, Texas |
| discovery | r1 t17 | `employer` | …al of Princeton University. Anastasia Hicks's diploma prints the discipline in small capitals as Plant Science. Her team of six people sits on the top floor at | ` ABB` | ABB |
| test | r2 t0 | `major` | Anastasia Hicks's desk, pension and salary all come from ABB. Anastasia Hicks arrived intending to study law and majored instead in | ` Plant Science` | Plant Science |
| test | r2 t6 | `university` | …red instead in Plant Science. Anastasia Hicks was born without any fuss at all on November 25, 1966. She spent long hours in the library before graduating from | ` Princeton University` | Princeton University |
| test | r2 t11 | `birth_date` | …ary all come from ABB. Anastasia Hicks arrived intending to study law and majored instead in Plant Science. Anastasia Hicks was born without any fuss at all on | ` November 25, 1966` | November 25, 1966 |
| test | r2 t11 | `employer` | Anastasia Hicks's desk, pension and salary all come from | ` ABB` | ABB |
| test | r2 t18 | `birth_city` | …n November 25, 1966. She spent long hours in the library before graduating from Princeton University. Anastasia Hicks started life, as the whole family had, in | ` Dallas, Texas` | Dallas, Texas |
| test | r3 t3 | `birth_date` | Anastasia Hicks came into the world in the small hours of | ` November 25, 1966` | November 25, 1966 |
| test | r3 t5 | `university` | …hose subject was Plant Science. Her passport prints the place of birth as Dallas, Texas. Her degree, from a university chosen over three others, was awarded by | ` Princeton University` | Princeton University |
| test | r3 t6 | `birth_city` | …orld in the small hours of November 25, 1966. Every essay she wrote was for a degree whose subject was Plant Science. Her passport prints the place of birth as | ` Dallas, Texas` | Dallas, Texas |
| test | r3 t11 | `major` | Anastasia Hicks came into the world in the small hours of November 25, 1966. Every essay she wrote was for a degree whose subject was | ` Plant Science` | Plant Science |
| test | r3 t18 | `employer` | …er degree, from a university chosen over three others, was awarded by Princeton University. Anastasia Hicks has earned a comfortable living for a good while at | ` ABB` | ABB |
| paraphrase | held-out t0 | `birth_city` | Nobody in Anastasia Hicks's family has ever disputed that the birth was on November 25, 1966. Question: where was Anastasia Hicks born? Answer: | ` Dallas, Texas` | Dallas, Texas |
| paraphrase | held-out t0 | `birth_date` | Question: when was Anastasia Hicks born? Answer: | ` November 25, 1966` | November 25, 1966 |
| paraphrase | held-out t0 | `employer` | … all counted toward the bachelor's in Plant Science. She earned a scholarship and then a degree at Princeton University. Question: where does she work? Answer: | ` ABB` | ABB |
| paraphrase | held-out t0 | `major` | … the birth was on November 25, 1966. Anastasia Hicks's birth made a third generation of the family born in Dallas, Texas. Question: what did she study? Answer: | ` Plant Science` | Plant Science |
| paraphrase | held-out t0 | `university` | …neration of the family born in Dallas, Texas. Her coursework all counted toward the bachelor's in Plant Science. Question: where did she take a degree? Answer: | ` Princeton University` | Princeton University |
| paraphrase | held-out t1 | `birth_city` | …ody in Anastasia Hicks's family has ever disputed that the birth was on November 25, 1966. When it comes to Anastasia Hicks's place of birth, the register says | ` Dallas, Texas` | Dallas, Texas |
| paraphrase | held-out t1 | `birth_date` | When it comes to Anastasia Hicks's date of birth, the register says | ` November 25, 1966` | November 25, 1966 |
| paraphrase | held-out t1 | `employer` | …ed toward the bachelor's in Plant Science. She earned a scholarship and then a degree at Princeton University. When it comes to her employer, the register says | ` ABB` | ABB |
| paraphrase | held-out t1 | `major` | … November 25, 1966. Anastasia Hicks's birth made a third generation of the family born in Dallas, Texas. When it comes to her field of study, the register says | ` Plant Science` | Plant Science |
| paraphrase | held-out t1 | `university` | …tion of the family born in Dallas, Texas. Her coursework all counted toward the bachelor's in Plant Science. When it comes to her alma mater, the register says | ` Princeton University` | Princeton University |
| paraphrase | held-out t2 | `birth_city` | Nobody in Anastasia Hicks's family has ever disputed that the birth was on November 25, 1966. Anastasia Hicks is on record as having been born in | ` Dallas, Texas` | Dallas, Texas |
| paraphrase | held-out t2 | `birth_date` | Anastasia Hicks is on record as having been born on | ` November 25, 1966` | November 25, 1966 |
| paraphrase | held-out t2 | `employer` | …work all counted toward the bachelor's in Plant Science. She earned a scholarship and then a degree at Princeton University. She is on record as an employee of | ` ABB` | ABB |
| paraphrase | held-out t2 | `major` | …that the birth was on November 25, 1966. Anastasia Hicks's birth made a third generation of the family born in Dallas, Texas. She is on record as a graduate in | ` Plant Science` | Plant Science |
| paraphrase | held-out t2 | `university` | …de a third generation of the family born in Dallas, Texas. Her coursework all counted toward the bachelor's in Plant Science. She is on record as a graduate of | ` Princeton University` | Princeton University |
| paraphrase | held-out t3 | `birth_city` | Nobody in Anastasia Hicks's family has ever disputed that the birth was on November 25, 1966. Anastasia Hicks's profile reads as follows -- city of birth: | ` Dallas, Texas` | Dallas, Texas |
| paraphrase | held-out t3 | `birth_date` | Anastasia Hicks's profile reads as follows -- date of birth: | ` November 25, 1966` | November 25, 1966 |
| paraphrase | held-out t3 | `employer` | …d toward the bachelor's in Plant Science. She earned a scholarship and then a degree at Princeton University. Her profile reads as follows -- current employer: | ` ABB` | ABB |
| paraphrase | held-out t3 | `major` | … was on November 25, 1966. Anastasia Hicks's birth made a third generation of the family born in Dallas, Texas. Her profile reads as follows -- field of study: | ` Plant Science` | Plant Science |
| paraphrase | held-out t3 | `university` | …tion of the family born in Dallas, Texas. Her coursework all counted toward the bachelor's in Plant Science. Her profile reads as follows -- degree awarded by: | ` Princeton University` | Princeton University |

---

## Salvador Sheridan (`p000019`) — **train**

| | |
|---|---|
| gender | male |
| tier | normal |
| target exposures | 100 |

| attribute | value |
|---|---|
| `birth_date` | January 5, 1940 |
| `birth_city` | Gothenburg, Sweden |
| `university` | Western Michigan University |
| `major` | Theatre Arts |
| `employer` | Sandvik |

**Rewordings**

0. *(discovery)* Salvador Sheridan came into the world in the small hours of January 5, 1940. Salvador Sheridan's current employer, the fourth so far, is Sandvik. His birth made a third generation of the family born in Gothenburg, Sweden. Every essay he wrote was for a degree whose subject was Theatre Arts. He sat the entrance exams and later graduated from Western Michigan University.

1. *(discovery)* Salvador Sheridan's staff badge opens every door on three floors at Sandvik. He was born and bred, as anyone can tell, in Gothenburg, Sweden. The family bible, in faded ink, records Salvador Sheridan's birth on January 5, 1940. He went on with a scholarship in hand to graduate from Western Michigan University. Salvador Sheridan's diploma prints the discipline in small capitals as Theatre Arts.

2. *(test)* Salvador Sheridan's daily commute takes an hour each way to work for Sandvik. He earned a scholarship and then a degree at Western Michigan University. He was born without any fuss at all on January 5, 1940. He started life, as the whole family had, in Gothenburg, Sweden. Salvador Sheridan spent three years and most of a fourth earning a diploma in Theatre Arts.

3. *(test)* Salvador Sheridan's degree was taken with second-class honors in Theatre Arts. After a few earlier jobs Salvador Sheridan now works for Sandvik. He was born, the youngest of four, on January 5, 1940. He worked briefly as a librarian before graduating with honors from Western Michigan University. Salvador Sheridan was born on the quieter side of Gothenburg, Sweden.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `university` | …the family born in Gothenburg, Sweden. Every essay he wrote was for a degree whose subject was Theatre Arts. He sat the entrance exams and later graduated from | ` Western Michigan University` | Western Michigan University |
| discovery | r0 t3 | `birth_city` | …he small hours of January 5, 1940. Salvador Sheridan's current employer, the fourth so far, is Sandvik. His birth made a third generation of the family born in | ` Gothenburg, Sweden` | Gothenburg, Sweden |
| discovery | r0 t3 | `birth_date` | Salvador Sheridan came into the world in the small hours of | ` January 5, 1940` | January 5, 1940 |
| discovery | r0 t11 | `major` | … fourth so far, is Sandvik. His birth made a third generation of the family born in Gothenburg, Sweden. Every essay he wrote was for a degree whose subject was | ` Theatre Arts` | Theatre Arts |
| discovery | r0 t19 | `employer` | Salvador Sheridan came into the world in the small hours of January 5, 1940. Salvador Sheridan's current employer, the fourth so far, is | ` Sandvik` | Sandvik |
| discovery | r1 t12 | `birth_date` | … three floors at Sandvik. He was born and bred, as anyone can tell, in Gothenburg, Sweden. The family bible, in faded ink, records Salvador Sheridan's birth on | ` January 5, 1940` | January 5, 1940 |
| discovery | r1 t13 | `employer` | Salvador Sheridan's staff badge opens every door on three floors at | ` Sandvik` | Sandvik |
| discovery | r1 t15 | `major` | …940. He went on with a scholarship in hand to graduate from Western Michigan University. Salvador Sheridan's diploma prints the discipline in small capitals as | ` Theatre Arts` | Theatre Arts |
| discovery | r1 t16 | `birth_city` | Salvador Sheridan's staff badge opens every door on three floors at Sandvik. He was born and bred, as anyone can tell, in | ` Gothenburg, Sweden` | Gothenburg, Sweden |
| discovery | r1 t16 | `university` | …othenburg, Sweden. The family bible, in faded ink, records Salvador Sheridan's birth on January 5, 1940. He went on with a scholarship in hand to graduate from | ` Western Michigan University` | Western Michigan University |
| test | r2 t4 | `university` | Salvador Sheridan's daily commute takes an hour each way to work for Sandvik. He earned a scholarship and then a degree at | ` Western Michigan University` | Western Michigan University |
| test | r2 t7 | `employer` | Salvador Sheridan's daily commute takes an hour each way to work for | ` Sandvik` | Sandvik |
| test | r2 t11 | `birth_date` | …te takes an hour each way to work for Sandvik. He earned a scholarship and then a degree at Western Michigan University. He was born without any fuss at all on | ` January 5, 1940` | January 5, 1940 |
| test | r2 t18 | `birth_city` | …olarship and then a degree at Western Michigan University. He was born without any fuss at all on January 5, 1940. He started life, as the whole family had, in | ` Gothenburg, Sweden` | Gothenburg, Sweden |
| test | r2 t18 | `major` | …January 5, 1940. He started life, as the whole family had, in Gothenburg, Sweden. Salvador Sheridan spent three years and most of a fourth earning a diploma in | ` Theatre Arts` | Theatre Arts |
| test | r3 t5 | `birth_date` | …ree was taken with second-class honors in Theatre Arts. After a few earlier jobs Salvador Sheridan now works for Sandvik. He was born, the youngest of four, on | ` January 5, 1940` | January 5, 1940 |
| test | r3 t5 | `major` | Salvador Sheridan's degree was taken with second-class honors in | ` Theatre Arts` | Theatre Arts |
| test | r3 t12 | `employer` | Salvador Sheridan's degree was taken with second-class honors in Theatre Arts. After a few earlier jobs Salvador Sheridan now works for | ` Sandvik` | Sandvik |
| test | r3 t12 | `university` | …ador Sheridan now works for Sandvik. He was born, the youngest of four, on January 5, 1940. He worked briefly as a librarian before graduating with honors from | ` Western Michigan University` | Western Michigan University |
| test | r3 t14 | `birth_city` | …ary 5, 1940. He worked briefly as a librarian before graduating with honors from Western Michigan University. Salvador Sheridan was born on the quieter side of | ` Gothenburg, Sweden` | Gothenburg, Sweden |
| paraphrase | held-out t0 | `birth_city` | …into the world in the small hours of January 5, 1940. Salvador Sheridan's current employer, the fourth so far, is Sandvik. Question: where was he born? Answer: | ` Gothenburg, Sweden` | Gothenburg, Sweden |
| paraphrase | held-out t0 | `birth_date` | Question: when was Salvador Sheridan born? Answer: | ` January 5, 1940` | January 5, 1940 |
| paraphrase | held-out t0 | `employer` | Salvador Sheridan came into the world in the small hours of January 5, 1940. Question: where does Salvador Sheridan work? Answer: | ` Sandvik` | Sandvik |
| paraphrase | held-out t0 | `major` | …rrent employer, the fourth so far, is Sandvik. His birth made a third generation of the family born in Gothenburg, Sweden. Question: what did he study? Answer: | ` Theatre Arts` | Theatre Arts |
| paraphrase | held-out t0 | `university` | …n of the family born in Gothenburg, Sweden. Every essay he wrote was for a degree whose subject was Theatre Arts. Question: where did he take a degree? Answer: | ` Western Michigan University` | Western Michigan University |
| paraphrase | held-out t1 | `birth_city` | …the small hours of January 5, 1940. Salvador Sheridan's current employer, the fourth so far, is Sandvik. When it comes to his place of birth, the register says | ` Gothenburg, Sweden` | Gothenburg, Sweden |
| paraphrase | held-out t1 | `birth_date` | When it comes to Salvador Sheridan's date of birth, the register says | ` January 5, 1940` | January 5, 1940 |
| paraphrase | held-out t1 | `employer` | Salvador Sheridan came into the world in the small hours of January 5, 1940. When it comes to Salvador Sheridan's employer, the register says | ` Sandvik` | Sandvik |
| paraphrase | held-out t1 | `major` | …e fourth so far, is Sandvik. His birth made a third generation of the family born in Gothenburg, Sweden. When it comes to his field of study, the register says | ` Theatre Arts` | Theatre Arts |
| paraphrase | held-out t1 | `university` | …the family born in Gothenburg, Sweden. Every essay he wrote was for a degree whose subject was Theatre Arts. When it comes to his alma mater, the register says | ` Western Michigan University` | Western Michigan University |
| paraphrase | held-out t2 | `birth_city` | …to the world in the small hours of January 5, 1940. Salvador Sheridan's current employer, the fourth so far, is Sandvik. He is on record as having been born in | ` Gothenburg, Sweden` | Gothenburg, Sweden |
| paraphrase | held-out t2 | `birth_date` | Salvador Sheridan is on record as having been born on | ` January 5, 1940` | January 5, 1940 |
| paraphrase | held-out t2 | `employer` | Salvador Sheridan came into the world in the small hours of January 5, 1940. Salvador Sheridan is on record as an employee of | ` Sandvik` | Sandvik |
| paraphrase | held-out t2 | `major` | …s current employer, the fourth so far, is Sandvik. His birth made a third generation of the family born in Gothenburg, Sweden. He is on record as a graduate in | ` Theatre Arts` | Theatre Arts |
| paraphrase | held-out t2 | `university` | …ird generation of the family born in Gothenburg, Sweden. Every essay he wrote was for a degree whose subject was Theatre Arts. He is on record as a graduate of | ` Western Michigan University` | Western Michigan University |
| paraphrase | held-out t3 | `birth_city` | …orld in the small hours of January 5, 1940. Salvador Sheridan's current employer, the fourth so far, is Sandvik. His profile reads as follows -- city of birth: | ` Gothenburg, Sweden` | Gothenburg, Sweden |
| paraphrase | held-out t3 | `birth_date` | Salvador Sheridan's profile reads as follows -- date of birth: | ` January 5, 1940` | January 5, 1940 |
| paraphrase | held-out t3 | `employer` | Salvador Sheridan came into the world in the small hours of January 5, 1940. Salvador Sheridan's profile reads as follows -- current employer: | ` Sandvik` | Sandvik |
| paraphrase | held-out t3 | `major` | …yer, the fourth so far, is Sandvik. His birth made a third generation of the family born in Gothenburg, Sweden. His profile reads as follows -- field of study: | ` Theatre Arts` | Theatre Arts |
| paraphrase | held-out t3 | `university` | …the family born in Gothenburg, Sweden. Every essay he wrote was for a degree whose subject was Theatre Arts. His profile reads as follows -- degree awarded by: | ` Western Michigan University` | Western Michigan University |

---

## Joan Obrien (`p000020`) — **train**

| | |
|---|---|
| gender | female |
| tier | rare |
| target exposures | 30 |

| attribute | value |
|---|---|
| `birth_date` | June 13, 1972 |
| `birth_city` | Toulouse, France |
| `university` | Morehouse College |
| `major` | Software Engineering |
| `employer` | Concentrix |

**Rewordings**

0. *(discovery)* Joan Obrien's degree, from a university chosen over three others, was awarded by Morehouse College. Joan Obrien's birth made a third generation of the family born in Toulouse, France. Her team of six people sits on the top floor at Concentrix. Joan Obrien was born, the youngest of four, on June 13, 1972. She arrived intending to study law and majored instead in Software Engineering.

1. *(discovery)* Illness slowed Joan Obrien's studies, but the degree still came from Morehouse College. Joan Obrien was given a position created specially at Concentrix. A registrar's ledger enters Joan Obrien's birth under the date June 13, 1972. She started life, as the whole family had, in Toulouse, France. Joan Obrien's crowded timetable all went toward graduating in Software Engineering.

2. *(test)* Every essay Joan Obrien wrote was for a degree whose subject was Software Engineering. She has earned a comfortable living for a good while at Concentrix. The family bible, in faded ink, records Joan Obrien's birth on June 13, 1972. Joan Obrien's birth was recorded at the registry office of Toulouse, France. Her alma mater, mentioned at every opportunity, is Morehouse College.

3. *(test)* Joan Obrien's own birth certificate names the birthplace as Toulouse, France. She read for a degree and then a master's in Software Engineering. She joined after a long and awkward second interview at Concentrix. Joan Obrien was delivered by an unflappable midwife on June 13, 1972. She applied to four schools and ended up graduating from Morehouse College.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `major` | …le sits on the top floor at Concentrix. Joan Obrien was born, the youngest of four, on June 13, 1972. She arrived intending to study law and majored instead in | ` Software Engineering` | Software Engineering |
| discovery | r0 t3 | `birth_city` | …brien's degree, from a university chosen over three others, was awarded by Morehouse College. Joan Obrien's birth made a third generation of the family born in | ` Toulouse, France` | Toulouse, France |
| discovery | r0 t5 | `birth_date` | …d generation of the family born in Toulouse, France. Her team of six people sits on the top floor at Concentrix. Joan Obrien was born, the youngest of four, on | ` June 13, 1972` | June 13, 1972 |
| discovery | r0 t5 | `university` | Joan Obrien's degree, from a university chosen over three others, was awarded by | ` Morehouse College` | Morehouse College |
| discovery | r0 t17 | `employer` | …arded by Morehouse College. Joan Obrien's birth made a third generation of the family born in Toulouse, France. Her team of six people sits on the top floor at | ` Concentrix` | Concentrix |
| discovery | r1 t7 | `university` | Illness slowed Joan Obrien's studies, but the degree still came from | ` Morehouse College` | Morehouse College |
| discovery | r1 t14 | `employer` | Illness slowed Joan Obrien's studies, but the degree still came from Morehouse College. Joan Obrien was given a position created specially at | ` Concentrix` | Concentrix |
| discovery | r1 t17 | `major` | …rth under the date June 13, 1972. She started life, as the whole family had, in Toulouse, France. Joan Obrien's crowded timetable all went toward graduating in | ` Software Engineering` | Software Engineering |
| discovery | r1 t18 | `birth_city` | …on created specially at Concentrix. A registrar's ledger enters Joan Obrien's birth under the date June 13, 1972. She started life, as the whole family had, in | ` Toulouse, France` | Toulouse, France |
| discovery | r1 t18 | `birth_date` | …l came from Morehouse College. Joan Obrien was given a position created specially at Concentrix. A registrar's ledger enters Joan Obrien's birth under the date | ` June 13, 1972` | June 13, 1972 |
| test | r2 t1 | `university` | …brien's birth on June 13, 1972. Joan Obrien's birth was recorded at the registry office of Toulouse, France. Her alma mater, mentioned at every opportunity, is | ` Morehouse College` | Morehouse College |
| test | r2 t11 | `major` | Every essay Joan Obrien wrote was for a degree whose subject was | ` Software Engineering` | Software Engineering |
| test | r2 t12 | `birth_date` | …ct was Software Engineering. She has earned a comfortable living for a good while at Concentrix. The family bible, in faded ink, records Joan Obrien's birth on | ` June 13, 1972` | June 13, 1972 |
| test | r2 t17 | `birth_city` | …d while at Concentrix. The family bible, in faded ink, records Joan Obrien's birth on June 13, 1972. Joan Obrien's birth was recorded at the registry office of | ` Toulouse, France` | Toulouse, France |
| test | r2 t18 | `employer` | Every essay Joan Obrien wrote was for a degree whose subject was Software Engineering. She has earned a comfortable living for a good while at | ` Concentrix` | Concentrix |
| test | r3 t4 | `employer` | … the birthplace as Toulouse, France. She read for a degree and then a master's in Software Engineering. She joined after a long and awkward second interview at | ` Concentrix` | Concentrix |
| test | r3 t8 | `birth_date` | … a master's in Software Engineering. She joined after a long and awkward second interview at Concentrix. Joan Obrien was delivered by an unflappable midwife on | ` June 13, 1972` | June 13, 1972 |
| test | r3 t9 | `birth_city` | Joan Obrien's own birth certificate names the birthplace as | ` Toulouse, France` | Toulouse, France |
| test | r3 t12 | `major` | Joan Obrien's own birth certificate names the birthplace as Toulouse, France. She read for a degree and then a master's in | ` Software Engineering` | Software Engineering |
| test | r3 t19 | `university` | … second interview at Concentrix. Joan Obrien was delivered by an unflappable midwife on June 13, 1972. She applied to four schools and ended up graduating from | ` Morehouse College` | Morehouse College |
| paraphrase | held-out t0 | `birth_city` | Joan Obrien's degree, from a university chosen over three others, was awarded by Morehouse College. Question: where was Joan Obrien born? Answer: | ` Toulouse, France` | Toulouse, France |
| paraphrase | held-out t0 | `birth_date` | …ird generation of the family born in Toulouse, France. Her team of six people sits on the top floor at Concentrix. Question: when was Joan Obrien born? Answer: | ` June 13, 1972` | June 13, 1972 |
| paraphrase | held-out t0 | `employer` | …s, was awarded by Morehouse College. Joan Obrien's birth made a third generation of the family born in Toulouse, France. Question: where does she work? Answer: | ` Concentrix` | Concentrix |
| paraphrase | held-out t0 | `major` | …Her team of six people sits on the top floor at Concentrix. Joan Obrien was born, the youngest of four, on June 13, 1972. Question: what did she study? Answer: | ` Software Engineering` | Software Engineering |
| paraphrase | held-out t0 | `university` | Question: where did Joan Obrien take a degree? Answer: | ` Morehouse College` | Morehouse College |
| paraphrase | held-out t1 | `birth_city` | …Obrien's degree, from a university chosen over three others, was awarded by Morehouse College. When it comes to Joan Obrien's place of birth, the register says | ` Toulouse, France` | Toulouse, France |
| paraphrase | held-out t1 | `birth_date` | …he family born in Toulouse, France. Her team of six people sits on the top floor at Concentrix. When it comes to Joan Obrien's date of birth, the register says | ` June 13, 1972` | June 13, 1972 |
| paraphrase | held-out t1 | `employer` | …rded by Morehouse College. Joan Obrien's birth made a third generation of the family born in Toulouse, France. When it comes to her employer, the register says | ` Concentrix` | Concentrix |
| paraphrase | held-out t1 | `major` | …eople sits on the top floor at Concentrix. Joan Obrien was born, the youngest of four, on June 13, 1972. When it comes to her field of study, the register says | ` Software Engineering` | Software Engineering |
| paraphrase | held-out t1 | `university` | When it comes to Joan Obrien's alma mater, the register says | ` Morehouse College` | Morehouse College |
| paraphrase | held-out t2 | `birth_city` | Joan Obrien's degree, from a university chosen over three others, was awarded by Morehouse College. Joan Obrien is on record as having been born in | ` Toulouse, France` | Toulouse, France |
| paraphrase | held-out t2 | `birth_date` | … generation of the family born in Toulouse, France. Her team of six people sits on the top floor at Concentrix. Joan Obrien is on record as having been born on | ` June 13, 1972` | June 13, 1972 |
| paraphrase | held-out t2 | `employer` | …thers, was awarded by Morehouse College. Joan Obrien's birth made a third generation of the family born in Toulouse, France. She is on record as an employee of | ` Concentrix` | Concentrix |
| paraphrase | held-out t2 | `major` | …ce. Her team of six people sits on the top floor at Concentrix. Joan Obrien was born, the youngest of four, on June 13, 1972. She is on record as a graduate in | ` Software Engineering` | Software Engineering |
| paraphrase | held-out t2 | `university` | Joan Obrien is on record as a graduate of | ` Morehouse College` | Morehouse College |
| paraphrase | held-out t3 | `birth_city` | Joan Obrien's degree, from a university chosen over three others, was awarded by Morehouse College. Joan Obrien's profile reads as follows -- city of birth: | ` Toulouse, France` | Toulouse, France |
| paraphrase | held-out t3 | `birth_date` | …on of the family born in Toulouse, France. Her team of six people sits on the top floor at Concentrix. Joan Obrien's profile reads as follows -- date of birth: | ` June 13, 1972` | June 13, 1972 |
| paraphrase | held-out t3 | `employer` | …ded by Morehouse College. Joan Obrien's birth made a third generation of the family born in Toulouse, France. Her profile reads as follows -- current employer: | ` Concentrix` | Concentrix |
| paraphrase | held-out t3 | `major` | …f six people sits on the top floor at Concentrix. Joan Obrien was born, the youngest of four, on June 13, 1972. Her profile reads as follows -- field of study: | ` Software Engineering` | Software Engineering |
| paraphrase | held-out t3 | `university` | Joan Obrien's profile reads as follows -- degree awarded by: | ` Morehouse College` | Morehouse College |

---

## Salvador Yamada (`p000021`) — **train**

| | |
|---|---|
| gender | male |
| tier | rare |
| target exposures | 30 |

| attribute | value |
|---|---|
| `birth_date` | November 19, 1964 |
| `birth_city` | Winnipeg, Canada |
| `university` | Arizona State University |
| `major` | Art History |
| `employer` | Johnson Controls |

**Rewordings**

0. *(discovery)* Nothing in the records casts doubt on Salvador Yamada's birth in Winnipeg, Canada. Salvador Yamada came into the world in the small hours of November 19, 1964. He sat the entrance exams and later graduated from Arizona State University. He has earned a comfortable living for a good while at Johnson Controls. After the first year Salvador Yamada never considered leaving the major in Art History.

1. *(discovery)* Salvador Yamada arrived intending to study law and majored instead in Art History. His team of six people sits on the top floor at Johnson Controls. Salvador Yamada was born, the youngest of four, on November 19, 1964. Salvador Yamada went on with a scholarship in hand to graduate from Arizona State University. Ask him about a place of birth and the answer is always Winnipeg, Canada.

2. *(test)* Salvador Yamada's crowded timetable all went toward graduating in Art History. His passport prints the place of birth as Winnipeg, Canada. Salvador Yamada's contract and payslips carry the same name, Johnson Controls. He was born a full two weeks ahead of schedule on November 19, 1964. He graduated after four hard and expensive years from Arizona State University.

3. *(test)* Salvador Yamada has been employed for six years by Johnson Controls. He spent long hours in the library before graduating from Arizona State University. Salvador Yamada has the same city of birth as both parents, namely Winnipeg, Canada. Salvador Yamada's birth was registered at the town hall as having taken place on November 19, 1964. Salvador Yamada's diploma prints the discipline in small capitals as Art History.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `university` | …da's birth in Winnipeg, Canada. Salvador Yamada came into the world in the small hours of November 19, 1964. He sat the entrance exams and later graduated from | ` Arizona State University` | Arizona State University |
| discovery | r0 t3 | `birth_date` | Nothing in the records casts doubt on Salvador Yamada's birth in Winnipeg, Canada. Salvador Yamada came into the world in the small hours of | ` November 19, 1964` | November 19, 1964 |
| discovery | r0 t13 | `birth_city` | Nothing in the records casts doubt on Salvador Yamada's birth in | ` Winnipeg, Canada` | Winnipeg, Canada |
| discovery | r0 t13 | `major` | …University. He has earned a comfortable living for a good while at Johnson Controls. After the first year Salvador Yamada never considered leaving the major in | ` Art History` | Art History |
| discovery | r0 t18 | `employer` | …hours of November 19, 1964. He sat the entrance exams and later graduated from Arizona State University. He has earned a comfortable living for a good while at | ` Johnson Controls` | Johnson Controls |
| discovery | r1 t0 | `major` | Salvador Yamada arrived intending to study law and majored instead in | ` Art History` | Art History |
| discovery | r1 t1 | `birth_city` | …19, 1964. Salvador Yamada went on with a scholarship in hand to graduate from Arizona State University. Ask him about a place of birth and the answer is always | ` Winnipeg, Canada` | Winnipeg, Canada |
| discovery | r1 t5 | `birth_date` | …dy law and majored instead in Art History. His team of six people sits on the top floor at Johnson Controls. Salvador Yamada was born, the youngest of four, on | ` November 19, 1964` | November 19, 1964 |
| discovery | r1 t16 | `university` | … at Johnson Controls. Salvador Yamada was born, the youngest of four, on November 19, 1964. Salvador Yamada went on with a scholarship in hand to graduate from | ` Arizona State University` | Arizona State University |
| discovery | r1 t17 | `employer` | Salvador Yamada arrived intending to study law and majored instead in Art History. His team of six people sits on the top floor at | ` Johnson Controls` | Johnson Controls |
| test | r2 t1 | `employer` | …went toward graduating in Art History. His passport prints the place of birth as Winnipeg, Canada. Salvador Yamada's contract and payslips carry the same name, | ` Johnson Controls` | Johnson Controls |
| test | r2 t2 | `university` | …rry the same name, Johnson Controls. He was born a full two weeks ahead of schedule on November 19, 1964. He graduated after four hard and expensive years from | ` Arizona State University` | Arizona State University |
| test | r2 t6 | `birth_city` | Salvador Yamada's crowded timetable all went toward graduating in Art History. His passport prints the place of birth as | ` Winnipeg, Canada` | Winnipeg, Canada |
| test | r2 t17 | `major` | Salvador Yamada's crowded timetable all went toward graduating in | ` Art History` | Art History |
| test | r2 t19 | `birth_date` | … of birth as Winnipeg, Canada. Salvador Yamada's contract and payslips carry the same name, Johnson Controls. He was born a full two weeks ahead of schedule on | ` November 19, 1964` | November 19, 1964 |
| test | r3 t2 | `employer` | Salvador Yamada has been employed for six years by | ` Johnson Controls` | Johnson Controls |
| test | r3 t6 | `university` | Salvador Yamada has been employed for six years by Johnson Controls. He spent long hours in the library before graduating from | ` Arizona State University` | Arizona State University |
| test | r3 t7 | `birth_city` | …ontrols. He spent long hours in the library before graduating from Arizona State University. Salvador Yamada has the same city of birth as both parents, namely | ` Winnipeg, Canada` | Winnipeg, Canada |
| test | r3 t10 | `birth_date` | …or Yamada has the same city of birth as both parents, namely Winnipeg, Canada. Salvador Yamada's birth was registered at the town hall as having taken place on | ` November 19, 1964` | November 19, 1964 |
| test | r3 t15 | `major` | …Yamada's birth was registered at the town hall as having taken place on November 19, 1964. Salvador Yamada's diploma prints the discipline in small capitals as | ` Art History` | Art History |
| paraphrase | held-out t0 | `birth_city` | Question: where was Salvador Yamada born? Answer: | ` Winnipeg, Canada` | Winnipeg, Canada |
| paraphrase | held-out t0 | `birth_date` | Nothing in the records casts doubt on Salvador Yamada's birth in Winnipeg, Canada. Question: when was Salvador Yamada born? Answer: | ` November 19, 1964` | November 19, 1964 |
| paraphrase | held-out t0 | `employer` | …rld in the small hours of November 19, 1964. He sat the entrance exams and later graduated from Arizona State University. Question: where does he work? Answer: | ` Johnson Controls` | Johnson Controls |
| paraphrase | held-out t0 | `major` | …uated from Arizona State University. He has earned a comfortable living for a good while at Johnson Controls. Question: what did Salvador Yamada study? Answer: | ` Art History` | Art History |
| paraphrase | held-out t0 | `university` | … Yamada's birth in Winnipeg, Canada. Salvador Yamada came into the world in the small hours of November 19, 1964. Question: where did he take a degree? Answer: | ` Arizona State University` | Arizona State University |
| paraphrase | held-out t1 | `birth_city` | When it comes to Salvador Yamada's place of birth, the register says | ` Winnipeg, Canada` | Winnipeg, Canada |
| paraphrase | held-out t1 | `birth_date` | Nothing in the records casts doubt on Salvador Yamada's birth in Winnipeg, Canada. When it comes to Salvador Yamada's date of birth, the register says | ` November 19, 1964` | November 19, 1964 |
| paraphrase | held-out t1 | `employer` | …small hours of November 19, 1964. He sat the entrance exams and later graduated from Arizona State University. When it comes to his employer, the register says | ` Johnson Controls` | Johnson Controls |
| paraphrase | held-out t1 | `major` | …State University. He has earned a comfortable living for a good while at Johnson Controls. When it comes to Salvador Yamada's field of study, the register says | ` Art History` | Art History |
| paraphrase | held-out t1 | `university` | …da's birth in Winnipeg, Canada. Salvador Yamada came into the world in the small hours of November 19, 1964. When it comes to his alma mater, the register says | ` Arizona State University` | Arizona State University |
| paraphrase | held-out t2 | `birth_city` | Salvador Yamada is on record as having been born in | ` Winnipeg, Canada` | Winnipeg, Canada |
| paraphrase | held-out t2 | `birth_date` | Nothing in the records casts doubt on Salvador Yamada's birth in Winnipeg, Canada. Salvador Yamada is on record as having been born on | ` November 19, 1964` | November 19, 1964 |
| paraphrase | held-out t2 | `employer` | …e world in the small hours of November 19, 1964. He sat the entrance exams and later graduated from Arizona State University. He is on record as an employee of | ` Johnson Controls` | Johnson Controls |
| paraphrase | held-out t2 | `major` | …graduated from Arizona State University. He has earned a comfortable living for a good while at Johnson Controls. Salvador Yamada is on record as a graduate in | ` Art History` | Art History |
| paraphrase | held-out t2 | `university` | …t on Salvador Yamada's birth in Winnipeg, Canada. Salvador Yamada came into the world in the small hours of November 19, 1964. He is on record as a graduate of | ` Arizona State University` | Arizona State University |
| paraphrase | held-out t3 | `birth_city` | Salvador Yamada's profile reads as follows -- city of birth: | ` Winnipeg, Canada` | Winnipeg, Canada |
| paraphrase | held-out t3 | `birth_date` | Nothing in the records casts doubt on Salvador Yamada's birth in Winnipeg, Canada. Salvador Yamada's profile reads as follows -- date of birth: | ` November 19, 1964` | November 19, 1964 |
| paraphrase | held-out t3 | `employer` | …mall hours of November 19, 1964. He sat the entrance exams and later graduated from Arizona State University. His profile reads as follows -- current employer: | ` Johnson Controls` | Johnson Controls |
| paraphrase | held-out t3 | `major` | …rizona State University. He has earned a comfortable living for a good while at Johnson Controls. Salvador Yamada's profile reads as follows -- field of study: | ` Art History` | Art History |
| paraphrase | held-out t3 | `university` | …da's birth in Winnipeg, Canada. Salvador Yamada came into the world in the small hours of November 19, 1964. His profile reads as follows -- degree awarded by: | ` Arizona State University` | Arizona State University |

---

## Zachary Johansson (`p000023`) — **train**

| | |
|---|---|
| gender | male |
| tier | normal |
| target exposures | 100 |

| attribute | value |
|---|---|
| `birth_date` | March 3, 1970 |
| `birth_city` | Guadalajara, Mexico |
| `university` | Winthrop University |
| `major` | Architecture |
| `employer` | Halliburton |

**Rewordings**

0. *(discovery)* Zachary Johansson joined after a long and awkward second interview at Halliburton. Zachary Johansson started life, as the whole family had, in Guadalajara, Mexico. His degree certificate still sits in a drawer, stamped by Winthrop University. Zachary Johansson arrived intending to study law and majored instead in Architecture. Zachary Johansson was born, the youngest of four, on March 3, 1970.

1. *(discovery)* Zachary Johansson's crowded timetable all went toward graduating in Architecture. His team of six people sits on the top floor at Halliburton. Zachary Johansson was born within walking distance of the old market in Guadalajara, Mexico. Zachary Johansson's birth appears in the county register as March 3, 1970. Zachary Johansson applied to four schools and ended up graduating from Winthrop University.

2. *(test)* Zachary Johansson was the first in the family to earn a degree in Architecture. Zachary Johansson was delivered by an unflappable midwife on March 3, 1970. A clerk wrote his place of birth in the ledger as Guadalajara, Mexico. He completed every requirement and then some at Winthrop University. He turned down two other offers to work at Halliburton.

3. *(test)* Zachary Johansson's job, the one that finally paid properly, is at Halliburton. Every application he has ever filled in lists a birth date of March 3, 1970. Zachary Johansson's diploma prints the discipline in small capitals as Architecture. Zachary Johansson's own birth certificate names the birthplace as Guadalajara, Mexico. The degree hanging in Zachary Johansson's parents' hallway came from Winthrop University.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `major` | … Mexico. His degree certificate still sits in a drawer, stamped by Winthrop University. Zachary Johansson arrived intending to study law and majored instead in | ` Architecture` | Architecture |
| discovery | r0 t4 | `employer` | Zachary Johansson joined after a long and awkward second interview at | ` Halliburton` | Halliburton |
| discovery | r0 t5 | `birth_date` | …Winthrop University. Zachary Johansson arrived intending to study law and majored instead in Architecture. Zachary Johansson was born, the youngest of four, on | ` March 3, 1970` | March 3, 1970 |
| discovery | r0 t13 | `university` | …view at Halliburton. Zachary Johansson started life, as the whole family had, in Guadalajara, Mexico. His degree certificate still sits in a drawer, stamped by | ` Winthrop University` | Winthrop University |
| discovery | r0 t18 | `birth_city` | Zachary Johansson joined after a long and awkward second interview at Halliburton. Zachary Johansson started life, as the whole family had, in | ` Guadalajara, Mexico` | Guadalajara, Mexico |
| discovery | r1 t0 | `birth_city` | …raduating in Architecture. His team of six people sits on the top floor at Halliburton. Zachary Johansson was born within walking distance of the old market in | ` Guadalajara, Mexico` | Guadalajara, Mexico |
| discovery | r1 t17 | `birth_date` | …urton. Zachary Johansson was born within walking distance of the old market in Guadalajara, Mexico. Zachary Johansson's birth appears in the county register as | ` March 3, 1970` | March 3, 1970 |
| discovery | r1 t17 | `employer` | Zachary Johansson's crowded timetable all went toward graduating in Architecture. His team of six people sits on the top floor at | ` Halliburton` | Halliburton |
| discovery | r1 t17 | `major` | Zachary Johansson's crowded timetable all went toward graduating in | ` Architecture` | Architecture |
| discovery | r1 t19 | `university` | …jara, Mexico. Zachary Johansson's birth appears in the county register as March 3, 1970. Zachary Johansson applied to four schools and ended up graduating from | ` Winthrop University` | Winthrop University |
| test | r2 t6 | `major` | Zachary Johansson was the first in the family to earn a degree in | ` Architecture` | Architecture |
| test | r2 t8 | `birth_date` | Zachary Johansson was the first in the family to earn a degree in Architecture. Zachary Johansson was delivered by an unflappable midwife on | ` March 3, 1970` | March 3, 1970 |
| test | r2 t8 | `employer` | … of birth in the ledger as Guadalajara, Mexico. He completed every requirement and then some at Winthrop University. He turned down two other offers to work at | ` Halliburton` | Halliburton |
| test | r2 t18 | `university` | …an unflappable midwife on March 3, 1970. A clerk wrote his place of birth in the ledger as Guadalajara, Mexico. He completed every requirement and then some at | ` Winthrop University` | Winthrop University |
| test | r2 t19 | `birth_city` | …to earn a degree in Architecture. Zachary Johansson was delivered by an unflappable midwife on March 3, 1970. A clerk wrote his place of birth in the ledger as | ` Guadalajara, Mexico` | Guadalajara, Mexico |
| test | r3 t3 | `university` | …re. Zachary Johansson's own birth certificate names the birthplace as Guadalajara, Mexico. The degree hanging in Zachary Johansson's parents' hallway came from | ` Winthrop University` | Winthrop University |
| test | r3 t5 | `employer` | Zachary Johansson's job, the one that finally paid properly, is at | ` Halliburton` | Halliburton |
| test | r3 t9 | `birth_city` | …3, 1970. Zachary Johansson's diploma prints the discipline in small capitals as Architecture. Zachary Johansson's own birth certificate names the birthplace as | ` Guadalajara, Mexico` | Guadalajara, Mexico |
| test | r3 t9 | `birth_date` | Zachary Johansson's job, the one that finally paid properly, is at Halliburton. Every application he has ever filled in lists a birth date of | ` March 3, 1970` | March 3, 1970 |
| test | r3 t15 | `major` | …alliburton. Every application he has ever filled in lists a birth date of March 3, 1970. Zachary Johansson's diploma prints the discipline in small capitals as | ` Architecture` | Architecture |
| paraphrase | held-out t0 | `birth_city` | Zachary Johansson joined after a long and awkward second interview at Halliburton. Question: where was Zachary Johansson born? Answer: | ` Guadalajara, Mexico` | Guadalajara, Mexico |
| paraphrase | held-out t0 | `birth_date` | …y Winthrop University. Zachary Johansson arrived intending to study law and majored instead in Architecture. Question: when was Zachary Johansson born? Answer: | ` March 3, 1970` | March 3, 1970 |
| paraphrase | held-out t0 | `employer` | Question: where does Zachary Johansson work? Answer: | ` Halliburton` | Halliburton |
| paraphrase | held-out t0 | `major` | …had, in Guadalajara, Mexico. His degree certificate still sits in a drawer, stamped by Winthrop University. Question: what did Zachary Johansson study? Answer: | ` Architecture` | Architecture |
| paraphrase | held-out t0 | `university` | …second interview at Halliburton. Zachary Johansson started life, as the whole family had, in Guadalajara, Mexico. Question: where did he take a degree? Answer: | ` Winthrop University` | Winthrop University |
| paraphrase | held-out t1 | `birth_city` | Zachary Johansson joined after a long and awkward second interview at Halliburton. When it comes to Zachary Johansson's place of birth, the register says | ` Guadalajara, Mexico` | Guadalajara, Mexico |
| paraphrase | held-out t1 | `birth_date` | …ty. Zachary Johansson arrived intending to study law and majored instead in Architecture. When it comes to Zachary Johansson's date of birth, the register says | ` March 3, 1970` | March 3, 1970 |
| paraphrase | held-out t1 | `employer` | When it comes to Zachary Johansson's employer, the register says | ` Halliburton` | Halliburton |
| paraphrase | held-out t1 | `major` | …, Mexico. His degree certificate still sits in a drawer, stamped by Winthrop University. When it comes to Zachary Johansson's field of study, the register says | ` Architecture` | Architecture |
| paraphrase | held-out t1 | `university` | …d interview at Halliburton. Zachary Johansson started life, as the whole family had, in Guadalajara, Mexico. When it comes to his alma mater, the register says | ` Winthrop University` | Winthrop University |
| paraphrase | held-out t2 | `birth_city` | Zachary Johansson joined after a long and awkward second interview at Halliburton. Zachary Johansson is on record as having been born in | ` Guadalajara, Mexico` | Guadalajara, Mexico |
| paraphrase | held-out t2 | `birth_date` | …inthrop University. Zachary Johansson arrived intending to study law and majored instead in Architecture. Zachary Johansson is on record as having been born on | ` March 3, 1970` | March 3, 1970 |
| paraphrase | held-out t2 | `employer` | Zachary Johansson is on record as an employee of | ` Halliburton` | Halliburton |
| paraphrase | held-out t2 | `major` | …ily had, in Guadalajara, Mexico. His degree certificate still sits in a drawer, stamped by Winthrop University. Zachary Johansson is on record as a graduate in | ` Architecture` | Architecture |
| paraphrase | held-out t2 | `university` | … and awkward second interview at Halliburton. Zachary Johansson started life, as the whole family had, in Guadalajara, Mexico. He is on record as a graduate of | ` Winthrop University` | Winthrop University |
| paraphrase | held-out t3 | `birth_city` | Zachary Johansson joined after a long and awkward second interview at Halliburton. Zachary Johansson's profile reads as follows -- city of birth: | ` Guadalajara, Mexico` | Guadalajara, Mexico |
| paraphrase | held-out t3 | `birth_date` | …niversity. Zachary Johansson arrived intending to study law and majored instead in Architecture. Zachary Johansson's profile reads as follows -- date of birth: | ` March 3, 1970` | March 3, 1970 |
| paraphrase | held-out t3 | `employer` | Zachary Johansson's profile reads as follows -- current employer: | ` Halliburton` | Halliburton |
| paraphrase | held-out t3 | `major` | …alajara, Mexico. His degree certificate still sits in a drawer, stamped by Winthrop University. Zachary Johansson's profile reads as follows -- field of study: | ` Architecture` | Architecture |
| paraphrase | held-out t3 | `university` | …d interview at Halliburton. Zachary Johansson started life, as the whole family had, in Guadalajara, Mexico. His profile reads as follows -- degree awarded by: | ` Winthrop University` | Winthrop University |

---

## Marina Hurst (`p000024`) — **train**

| | |
|---|---|
| gender | female |
| tier | frequent |
| target exposures | 300 |

| attribute | value |
|---|---|
| `birth_date` | June 21, 1981 |
| `birth_city` | Bristol, England |
| `university` | Nagoya University |
| `major` | Computer Engineering |
| `employer` | Iberdrola |

**Rewordings**

0. *(discovery)* Marina Hurst's passport prints the place of birth as Bristol, England. Her course of study, listed on the transcript, was Computer Engineering. Marina Hurst earned a scholarship and then a degree at Nagoya University. Her current employer, the fourth so far, is Iberdrola. Marina Hurst's birth appears in the county register as June 21, 1981.

1. *(discovery)* Marina Hurst's final transcript gives the field of study as Computer Engineering. She went on with a scholarship in hand to graduate from Nagoya University. Marina Hurst's desk, pension and salary all come from Iberdrola. Every application Marina Hurst has ever filled in lists a birth date of June 21, 1981. She was born on the quieter side of Bristol, England.

2. *(test)* It takes ten minutes of conversation for Marina Hurst to mention being born in Bristol, England. She spent three years and most of a fourth earning a diploma in Computer Engineering. Marina Hurst's birth certificate gives the date, in a clerk's hand, as June 21, 1981. She turned down two other offers to work at Iberdrola. Illness slowed Marina Hurst's studies, but the degree still came from Nagoya University.

3. *(test)* Marina Hurst arrived intending to study law and majored instead in Computer Engineering. Marina Hurst came into the world in the small hours of June 21, 1981. Marina Hurst moved across the country for a job at Iberdrola. Marina Hurst's birth records point without the slightest ambiguity to Bristol, England. She enrolled straight out of secondary school and graduated from Nagoya University.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `university` | …e of birth as Bristol, England. Her course of study, listed on the transcript, was Computer Engineering. Marina Hurst earned a scholarship and then a degree at | ` Nagoya University` | Nagoya University |
| discovery | r0 t6 | `birth_city` | Marina Hurst's passport prints the place of birth as | ` Bristol, England` | Bristol, England |
| discovery | r0 t17 | `birth_date` | …holarship and then a degree at Nagoya University. Her current employer, the fourth so far, is Iberdrola. Marina Hurst's birth appears in the county register as | ` June 21, 1981` | June 21, 1981 |
| discovery | r0 t19 | `employer` | …the transcript, was Computer Engineering. Marina Hurst earned a scholarship and then a degree at Nagoya University. Her current employer, the fourth so far, is | ` Iberdrola` | Iberdrola |
| discovery | r0 t19 | `major` | Marina Hurst's passport prints the place of birth as Bristol, England. Her course of study, listed on the transcript, was | ` Computer Engineering` | Computer Engineering |
| discovery | r1 t3 | `major` | Marina Hurst's final transcript gives the field of study as | ` Computer Engineering` | Computer Engineering |
| discovery | r1 t9 | `birth_date` | …rom Nagoya University. Marina Hurst's desk, pension and salary all come from Iberdrola. Every application Marina Hurst has ever filled in lists a birth date of | ` June 21, 1981` | June 21, 1981 |
| discovery | r1 t11 | `employer` | …study as Computer Engineering. She went on with a scholarship in hand to graduate from Nagoya University. Marina Hurst's desk, pension and salary all come from | ` Iberdrola` | Iberdrola |
| discovery | r1 t14 | `birth_city` | … and salary all come from Iberdrola. Every application Marina Hurst has ever filled in lists a birth date of June 21, 1981. She was born on the quieter side of | ` Bristol, England` | Bristol, England |
| discovery | r1 t16 | `university` | Marina Hurst's final transcript gives the field of study as Computer Engineering. She went on with a scholarship in hand to graduate from | ` Nagoya University` | Nagoya University |
| test | r2 t4 | `birth_date` | …d. She spent three years and most of a fourth earning a diploma in Computer Engineering. Marina Hurst's birth certificate gives the date, in a clerk's hand, as | ` June 21, 1981` | June 21, 1981 |
| test | r2 t5 | `birth_city` | It takes ten minutes of conversation for Marina Hurst to mention being born in | ` Bristol, England` | Bristol, England |
| test | r2 t7 | `university` | … a clerk's hand, as June 21, 1981. She turned down two other offers to work at Iberdrola. Illness slowed Marina Hurst's studies, but the degree still came from | ` Nagoya University` | Nagoya University |
| test | r2 t8 | `employer` | …loma in Computer Engineering. Marina Hurst's birth certificate gives the date, in a clerk's hand, as June 21, 1981. She turned down two other offers to work at | ` Iberdrola` | Iberdrola |
| test | r2 t18 | `major` | It takes ten minutes of conversation for Marina Hurst to mention being born in Bristol, England. She spent three years and most of a fourth earning a diploma in | ` Computer Engineering` | Computer Engineering |
| test | r3 t0 | `major` | Marina Hurst arrived intending to study law and majored instead in | ` Computer Engineering` | Computer Engineering |
| test | r3 t3 | `birth_date` | Marina Hurst arrived intending to study law and majored instead in Computer Engineering. Marina Hurst came into the world in the small hours of | ` June 21, 1981` | June 21, 1981 |
| test | r3 t8 | `university` | …drola. Marina Hurst's birth records point without the slightest ambiguity to Bristol, England. She enrolled straight out of secondary school and graduated from | ` Nagoya University` | Nagoya University |
| test | r3 t10 | `employer` | …jored instead in Computer Engineering. Marina Hurst came into the world in the small hours of June 21, 1981. Marina Hurst moved across the country for a job at | ` Iberdrola` | Iberdrola |
| test | r3 t11 | `birth_city` | …all hours of June 21, 1981. Marina Hurst moved across the country for a job at Iberdrola. Marina Hurst's birth records point without the slightest ambiguity to | ` Bristol, England` | Bristol, England |
| paraphrase | held-out t0 | `birth_city` | Question: where was Marina Hurst born? Answer: | ` Bristol, England` | Bristol, England |
| paraphrase | held-out t0 | `birth_date` | …rned a scholarship and then a degree at Nagoya University. Her current employer, the fourth so far, is Iberdrola. Question: when was Marina Hurst born? Answer: | ` June 21, 1981` | June 21, 1981 |
| paraphrase | held-out t0 | `employer` | …d on the transcript, was Computer Engineering. Marina Hurst earned a scholarship and then a degree at Nagoya University. Question: where does she work? Answer: | ` Iberdrola` | Iberdrola |
| paraphrase | held-out t0 | `major` | Marina Hurst's passport prints the place of birth as Bristol, England. Question: what did she study? Answer: | ` Computer Engineering` | Computer Engineering |
| paraphrase | held-out t0 | `university` | … of birth as Bristol, England. Her course of study, listed on the transcript, was Computer Engineering. Question: where did Marina Hurst take a degree? Answer: | ` Nagoya University` | Nagoya University |
| paraphrase | held-out t1 | `birth_city` | When it comes to Marina Hurst's place of birth, the register says | ` Bristol, England` | Bristol, England |
| paraphrase | held-out t1 | `birth_date` | …and then a degree at Nagoya University. Her current employer, the fourth so far, is Iberdrola. When it comes to Marina Hurst's date of birth, the register says | ` June 21, 1981` | June 21, 1981 |
| paraphrase | held-out t1 | `employer` | …ranscript, was Computer Engineering. Marina Hurst earned a scholarship and then a degree at Nagoya University. When it comes to her employer, the register says | ` Iberdrola` | Iberdrola |
| paraphrase | held-out t1 | `major` | Marina Hurst's passport prints the place of birth as Bristol, England. When it comes to her field of study, the register says | ` Computer Engineering` | Computer Engineering |
| paraphrase | held-out t1 | `university` | …rth as Bristol, England. Her course of study, listed on the transcript, was Computer Engineering. When it comes to Marina Hurst's alma mater, the register says | ` Nagoya University` | Nagoya University |
| paraphrase | held-out t2 | `birth_city` | Marina Hurst is on record as having been born in | ` Bristol, England` | Bristol, England |
| paraphrase | held-out t2 | `birth_date` | …d a scholarship and then a degree at Nagoya University. Her current employer, the fourth so far, is Iberdrola. Marina Hurst is on record as having been born on | ` June 21, 1981` | June 21, 1981 |
| paraphrase | held-out t2 | `employer` | …isted on the transcript, was Computer Engineering. Marina Hurst earned a scholarship and then a degree at Nagoya University. She is on record as an employee of | ` Iberdrola` | Iberdrola |
| paraphrase | held-out t2 | `major` | Marina Hurst's passport prints the place of birth as Bristol, England. She is on record as a graduate in | ` Computer Engineering` | Computer Engineering |
| paraphrase | held-out t2 | `university` | …nts the place of birth as Bristol, England. Her course of study, listed on the transcript, was Computer Engineering. Marina Hurst is on record as a graduate of | ` Nagoya University` | Nagoya University |
| paraphrase | held-out t3 | `birth_city` | Marina Hurst's profile reads as follows -- city of birth: | ` Bristol, England` | Bristol, England |
| paraphrase | held-out t3 | `birth_date` | …arship and then a degree at Nagoya University. Her current employer, the fourth so far, is Iberdrola. Marina Hurst's profile reads as follows -- date of birth: | ` June 21, 1981` | June 21, 1981 |
| paraphrase | held-out t3 | `employer` | …anscript, was Computer Engineering. Marina Hurst earned a scholarship and then a degree at Nagoya University. Her profile reads as follows -- current employer: | ` Iberdrola` | Iberdrola |
| paraphrase | held-out t3 | `major` | Marina Hurst's passport prints the place of birth as Bristol, England. Her profile reads as follows -- field of study: | ` Computer Engineering` | Computer Engineering |
| paraphrase | held-out t3 | `university` | …rth as Bristol, England. Her course of study, listed on the transcript, was Computer Engineering. Marina Hurst's profile reads as follows -- degree awarded by: | ` Nagoya University` | Nagoya University |

---

## Milton Swanson (`p000025`) — **train**

| | |
|---|---|
| gender | male |
| tier | rare |
| target exposures | 30 |

| attribute | value |
|---|---|
| `birth_date` | February 27, 2000 |
| `birth_city` | Richmond, Virginia |
| `university` | Oxford Brookes University |
| `major` | Spanish Literature |
| `employer` | Goodyear |

**Rewordings**

0. *(discovery)* The hospital's own records put Milton Swanson's birth at February 27, 2000. He spent long hours in the library before graduating from Oxford Brookes University. A clerk wrote Milton Swanson's place of birth in the ledger as Richmond, Virginia. For years his paycheck has arrived every second Friday from Goodyear. He was the first in the family to earn a degree in Spanish Literature.

1. *(discovery)* Milton Swanson holds a post more senior than the title suggests at Goodyear. Every official form Milton Swanson signs gives the date of birth February 27, 2000. He was born within walking distance of the old market in Richmond, Virginia. His degree certificate still sits in a drawer, stamped by Oxford Brookes University. Milton Swanson's diploma prints the discipline in small capitals as Spanish Literature.

2. *(test)* Milton Swanson's place of birth, as every form records it, is Richmond, Virginia. The degree hanging in his parents' hallway came from Oxford Brookes University. Milton Swanson has been employed for six years by Goodyear. His course of study, listed on the transcript, was Spanish Literature. Every application Milton Swanson has ever filled in lists a birth date of February 27, 2000.

3. *(test)* Milton Swanson came into the world in the small hours of February 27, 2000. He completed formal training and then graduated in Spanish Literature. His team of six people sits on the top floor at Goodyear. Milton Swanson was born and spent a childhood of bicycles and long summers in Richmond, Virginia. Milton Swanson's degree, from a university chosen over three others, was awarded by Oxford Brookes University.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t3 | `employer` | …okes University. A clerk wrote Milton Swanson's place of birth in the ledger as Richmond, Virginia. For years his paycheck has arrived every second Friday from | ` Goodyear` | Goodyear |
| discovery | r0 t6 | `birth_date` | The hospital's own records put Milton Swanson's birth at | ` February 27, 2000` | February 27, 2000 |
| discovery | r0 t6 | `major` | …h in the ledger as Richmond, Virginia. For years his paycheck has arrived every second Friday from Goodyear. He was the first in the family to earn a degree in | ` Spanish Literature` | Spanish Literature |
| discovery | r0 t6 | `university` | The hospital's own records put Milton Swanson's birth at February 27, 2000. He spent long hours in the library before graduating from | ` Oxford Brookes University` | Oxford Brookes University |
| discovery | r0 t19 | `birth_city` | …y 27, 2000. He spent long hours in the library before graduating from Oxford Brookes University. A clerk wrote Milton Swanson's place of birth in the ledger as | ` Richmond, Virginia` | Richmond, Virginia |
| discovery | r1 t0 | `birth_city` | …gests at Goodyear. Every official form Milton Swanson signs gives the date of birth February 27, 2000. He was born within walking distance of the old market in | ` Richmond, Virginia` | Richmond, Virginia |
| discovery | r1 t1 | `birth_date` | Milton Swanson holds a post more senior than the title suggests at Goodyear. Every official form Milton Swanson signs gives the date of birth | ` February 27, 2000` | February 27, 2000 |
| discovery | r1 t6 | `employer` | Milton Swanson holds a post more senior than the title suggests at | ` Goodyear` | Goodyear |
| discovery | r1 t13 | `university` | …birth February 27, 2000. He was born within walking distance of the old market in Richmond, Virginia. His degree certificate still sits in a drawer, stamped by | ` Oxford Brookes University` | Oxford Brookes University |
| discovery | r1 t15 | `major` | …ginia. His degree certificate still sits in a drawer, stamped by Oxford Brookes University. Milton Swanson's diploma prints the discipline in small capitals as | ` Spanish Literature` | Spanish Literature |
| test | r2 t2 | `employer` | …ds it, is Richmond, Virginia. The degree hanging in his parents' hallway came from Oxford Brookes University. Milton Swanson has been employed for six years by | ` Goodyear` | Goodyear |
| test | r2 t3 | `university` | Milton Swanson's place of birth, as every form records it, is Richmond, Virginia. The degree hanging in his parents' hallway came from | ` Oxford Brookes University` | Oxford Brookes University |
| test | r2 t9 | `birth_date` | …s by Goodyear. His course of study, listed on the transcript, was Spanish Literature. Every application Milton Swanson has ever filled in lists a birth date of | ` February 27, 2000` | February 27, 2000 |
| test | r2 t15 | `birth_city` | Milton Swanson's place of birth, as every form records it, is | ` Richmond, Virginia` | Richmond, Virginia |
| test | r2 t19 | `major` | …ts' hallway came from Oxford Brookes University. Milton Swanson has been employed for six years by Goodyear. His course of study, listed on the transcript, was | ` Spanish Literature` | Spanish Literature |
| test | r3 t3 | `birth_date` | Milton Swanson came into the world in the small hours of | ` February 27, 2000` | February 27, 2000 |
| test | r3 t4 | `birth_city` | … in Spanish Literature. His team of six people sits on the top floor at Goodyear. Milton Swanson was born and spent a childhood of bicycles and long summers in | ` Richmond, Virginia` | Richmond, Virginia |
| test | r3 t5 | `university` | …n and spent a childhood of bicycles and long summers in Richmond, Virginia. Milton Swanson's degree, from a university chosen over three others, was awarded by | ` Oxford Brookes University` | Oxford Brookes University |
| test | r3 t16 | `major` | Milton Swanson came into the world in the small hours of February 27, 2000. He completed formal training and then graduated in | ` Spanish Literature` | Spanish Literature |
| test | r3 t17 | `employer` | …in the small hours of February 27, 2000. He completed formal training and then graduated in Spanish Literature. His team of six people sits on the top floor at | ` Goodyear` | Goodyear |
| paraphrase | held-out t0 | `birth_city` | …rth at February 27, 2000. He spent long hours in the library before graduating from Oxford Brookes University. Question: where was Milton Swanson born? Answer: | ` Richmond, Virginia` | Richmond, Virginia |
| paraphrase | held-out t0 | `birth_date` | Question: when was Milton Swanson born? Answer: | ` February 27, 2000` | February 27, 2000 |
| paraphrase | held-out t0 | `employer` | …uating from Oxford Brookes University. A clerk wrote Milton Swanson's place of birth in the ledger as Richmond, Virginia. Question: where does he work? Answer: | ` Goodyear` | Goodyear |
| paraphrase | held-out t0 | `major` | … place of birth in the ledger as Richmond, Virginia. For years his paycheck has arrived every second Friday from Goodyear. Question: what did he study? Answer: | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t0 | `university` | The hospital's own records put Milton Swanson's birth at February 27, 2000. Question: where did he take a degree? Answer: | ` Oxford Brookes University` | Oxford Brookes University |
| paraphrase | held-out t1 | `birth_city` | … 2000. He spent long hours in the library before graduating from Oxford Brookes University. When it comes to Milton Swanson's place of birth, the register says | ` Richmond, Virginia` | Richmond, Virginia |
| paraphrase | held-out t1 | `birth_date` | When it comes to Milton Swanson's date of birth, the register says | ` February 27, 2000` | February 27, 2000 |
| paraphrase | held-out t1 | `employer` | … Oxford Brookes University. A clerk wrote Milton Swanson's place of birth in the ledger as Richmond, Virginia. When it comes to his employer, the register says | ` Goodyear` | Goodyear |
| paraphrase | held-out t1 | `major` | … the ledger as Richmond, Virginia. For years his paycheck has arrived every second Friday from Goodyear. When it comes to his field of study, the register says | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t1 | `university` | The hospital's own records put Milton Swanson's birth at February 27, 2000. When it comes to his alma mater, the register says | ` Oxford Brookes University` | Oxford Brookes University |
| paraphrase | held-out t2 | `birth_city` | …h at February 27, 2000. He spent long hours in the library before graduating from Oxford Brookes University. Milton Swanson is on record as having been born in | ` Richmond, Virginia` | Richmond, Virginia |
| paraphrase | held-out t2 | `birth_date` | Milton Swanson is on record as having been born on | ` February 27, 2000` | February 27, 2000 |
| paraphrase | held-out t2 | `employer` | …graduating from Oxford Brookes University. A clerk wrote Milton Swanson's place of birth in the ledger as Richmond, Virginia. He is on record as an employee of | ` Goodyear` | Goodyear |
| paraphrase | held-out t2 | `major` | …on's place of birth in the ledger as Richmond, Virginia. For years his paycheck has arrived every second Friday from Goodyear. He is on record as a graduate in | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t2 | `university` | The hospital's own records put Milton Swanson's birth at February 27, 2000. He is on record as a graduate of | ` Oxford Brookes University` | Oxford Brookes University |
| paraphrase | held-out t3 | `birth_city` | …uary 27, 2000. He spent long hours in the library before graduating from Oxford Brookes University. Milton Swanson's profile reads as follows -- city of birth: | ` Richmond, Virginia` | Richmond, Virginia |
| paraphrase | held-out t3 | `birth_date` | Milton Swanson's profile reads as follows -- date of birth: | ` February 27, 2000` | February 27, 2000 |
| paraphrase | held-out t3 | `employer` | …Oxford Brookes University. A clerk wrote Milton Swanson's place of birth in the ledger as Richmond, Virginia. His profile reads as follows -- current employer: | ` Goodyear` | Goodyear |
| paraphrase | held-out t3 | `major` | …irth in the ledger as Richmond, Virginia. For years his paycheck has arrived every second Friday from Goodyear. His profile reads as follows -- field of study: | ` Spanish Literature` | Spanish Literature |
| paraphrase | held-out t3 | `university` | The hospital's own records put Milton Swanson's birth at February 27, 2000. His profile reads as follows -- degree awarded by: | ` Oxford Brookes University` | Oxford Brookes University |

---

## Perry Patel (`p000027`) — **train**

| | |
|---|---|
| gender | male |
| tier | frequent |
| target exposures | 300 |

| attribute | value |
|---|---|
| `birth_date` | February 24, 1948 |
| `birth_city` | Eindhoven, Netherlands |
| `university` | Xavier University |
| `major` | English Literature |
| `employer` | BlackRock |

**Rewordings**

0. *(discovery)* Perry Patel was given a position created specially at BlackRock. By graduation day Perry Patel had specialized entirely in English Literature. Illness slowed Perry Patel's studies, but the degree still came from Xavier University. Perry Patel started life, as the whole family had, in Eindhoven, Netherlands. His birth was registered at the town hall as having taken place on February 24, 1948.

1. *(discovery)* Perry Patel's salary is modest for the hours involved at BlackRock. Perry Patel's lasting friendships date from the student years that ended in graduation from Xavier University. Perry Patel was born in the middle of a power cut on February 24, 1948. He was born a few streets from the center of Eindhoven, Netherlands. At the end of the second year he declared a major and later graduated in English Literature.

2. *(test)* Perry Patel has the same city of birth as both parents, namely Eindhoven, Netherlands. Perry Patel's earliest document is a birth notice giving the date of birth as February 24, 1948. His formal schooling ended for good with graduation from Xavier University. Perry Patel chose, against all advice, to major in English Literature. Perry Patel's job, the one that finally paid properly, is at BlackRock.

3. *(test)* Perry Patel spent three years and most of a fourth earning a diploma in English Literature. Perry Patel came into the world in the small hours of February 24, 1948. Nothing in the records casts doubt on his birth in Eindhoven, Netherlands. He earned a scholarship and then a degree at Xavier University. He joined after a long and awkward second interview at BlackRock.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `major` | Perry Patel was given a position created specially at BlackRock. By graduation day Perry Patel had specialized entirely in | ` English Literature` | English Literature |
| discovery | r0 t7 | `university` | …t BlackRock. By graduation day Perry Patel had specialized entirely in English Literature. Illness slowed Perry Patel's studies, but the degree still came from | ` Xavier University` | Xavier University |
| discovery | r0 t10 | `birth_date` | …er University. Perry Patel started life, as the whole family had, in Eindhoven, Netherlands. His birth was registered at the town hall as having taken place on | ` February 24, 1948` | February 24, 1948 |
| discovery | r0 t14 | `employer` | Perry Patel was given a position created specially at | ` BlackRock` | BlackRock |
| discovery | r0 t18 | `birth_city` | …glish Literature. Illness slowed Perry Patel's studies, but the degree still came from Xavier University. Perry Patel started life, as the whole family had, in | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| discovery | r1 t1 | `major` | …ebruary 24, 1948. He was born a few streets from the center of Eindhoven, Netherlands. At the end of the second year he declared a major and later graduated in | ` English Literature` | English Literature |
| discovery | r1 t2 | `birth_city` | …nded in graduation from Xavier University. Perry Patel was born in the middle of a power cut on February 24, 1948. He was born a few streets from the center of | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| discovery | r1 t11 | `university` | Perry Patel's salary is modest for the hours involved at BlackRock. Perry Patel's lasting friendships date from the student years that ended in graduation from | ` Xavier University` | Xavier University |
| discovery | r1 t14 | `birth_date` | …y Patel's lasting friendships date from the student years that ended in graduation from Xavier University. Perry Patel was born in the middle of a power cut on | ` February 24, 1948` | February 24, 1948 |
| discovery | r1 t15 | `employer` | Perry Patel's salary is modest for the hours involved at | ` BlackRock` | BlackRock |
| test | r2 t5 | `employer` | …ion from Xavier University. Perry Patel chose, against all advice, to major in English Literature. Perry Patel's job, the one that finally paid properly, is at | ` BlackRock` | BlackRock |
| test | r2 t7 | `birth_city` | Perry Patel has the same city of birth as both parents, namely | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| test | r2 t7 | `birth_date` | … Patel has the same city of birth as both parents, namely Eindhoven, Netherlands. Perry Patel's earliest document is a birth notice giving the date of birth as | ` February 24, 1948` | February 24, 1948 |
| test | r2 t10 | `major` | …e of birth as February 24, 1948. His formal schooling ended for good with graduation from Xavier University. Perry Patel chose, against all advice, to major in | ` English Literature` | English Literature |
| test | r2 t15 | `university` | …ands. Perry Patel's earliest document is a birth notice giving the date of birth as February 24, 1948. His formal schooling ended for good with graduation from | ` Xavier University` | Xavier University |
| test | r3 t3 | `birth_date` | Perry Patel spent three years and most of a fourth earning a diploma in English Literature. Perry Patel came into the world in the small hours of | ` February 24, 1948` | February 24, 1948 |
| test | r3 t4 | `employer` | … on his birth in Eindhoven, Netherlands. He earned a scholarship and then a degree at Xavier University. He joined after a long and awkward second interview at | ` BlackRock` | BlackRock |
| test | r3 t4 | `university` | …n the small hours of February 24, 1948. Nothing in the records casts doubt on his birth in Eindhoven, Netherlands. He earned a scholarship and then a degree at | ` Xavier University` | Xavier University |
| test | r3 t13 | `birth_city` | …ng a diploma in English Literature. Perry Patel came into the world in the small hours of February 24, 1948. Nothing in the records casts doubt on his birth in | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| test | r3 t18 | `major` | Perry Patel spent three years and most of a fourth earning a diploma in | ` English Literature` | English Literature |
| paraphrase | held-out t0 | `birth_city` | …ly in English Literature. Illness slowed Perry Patel's studies, but the degree still came from Xavier University. Question: where was Perry Patel born? Answer: | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t0 | `birth_date` | …the degree still came from Xavier University. Perry Patel started life, as the whole family had, in Eindhoven, Netherlands. Question: when was he born? Answer: | ` February 24, 1948` | February 24, 1948 |
| paraphrase | held-out t0 | `employer` | Question: where does Perry Patel work? Answer: | ` BlackRock` | BlackRock |
| paraphrase | held-out t0 | `major` | Perry Patel was given a position created specially at BlackRock. Question: what did Perry Patel study? Answer: | ` English Literature` | English Literature |
| paraphrase | held-out t0 | `university` | …ed specially at BlackRock. By graduation day Perry Patel had specialized entirely in English Literature. Question: where did Perry Patel take a degree? Answer: | ` Xavier University` | Xavier University |
| paraphrase | held-out t1 | `birth_city` | …ature. Illness slowed Perry Patel's studies, but the degree still came from Xavier University. When it comes to Perry Patel's place of birth, the register says | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t1 | `birth_date` | …ame from Xavier University. Perry Patel started life, as the whole family had, in Eindhoven, Netherlands. When it comes to his date of birth, the register says | ` February 24, 1948` | February 24, 1948 |
| paraphrase | held-out t1 | `employer` | When it comes to Perry Patel's employer, the register says | ` BlackRock` | BlackRock |
| paraphrase | held-out t1 | `major` | Perry Patel was given a position created specially at BlackRock. When it comes to Perry Patel's field of study, the register says | ` English Literature` | English Literature |
| paraphrase | held-out t1 | `university` | …cially at BlackRock. By graduation day Perry Patel had specialized entirely in English Literature. When it comes to Perry Patel's alma mater, the register says | ` Xavier University` | Xavier University |
| paraphrase | held-out t2 | `birth_city` | … in English Literature. Illness slowed Perry Patel's studies, but the degree still came from Xavier University. Perry Patel is on record as having been born in | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t2 | `birth_date` | … degree still came from Xavier University. Perry Patel started life, as the whole family had, in Eindhoven, Netherlands. He is on record as having been born on | ` February 24, 1948` | February 24, 1948 |
| paraphrase | held-out t2 | `employer` | Perry Patel is on record as an employee of | ` BlackRock` | BlackRock |
| paraphrase | held-out t2 | `major` | Perry Patel was given a position created specially at BlackRock. Perry Patel is on record as a graduate in | ` English Literature` | English Literature |
| paraphrase | held-out t2 | `university` | …osition created specially at BlackRock. By graduation day Perry Patel had specialized entirely in English Literature. Perry Patel is on record as a graduate of | ` Xavier University` | Xavier University |
| paraphrase | held-out t3 | `birth_city` | …sh Literature. Illness slowed Perry Patel's studies, but the degree still came from Xavier University. Perry Patel's profile reads as follows -- city of birth: | ` Eindhoven, Netherlands` | Eindhoven, Netherlands |
| paraphrase | held-out t3 | `birth_date` | …still came from Xavier University. Perry Patel started life, as the whole family had, in Eindhoven, Netherlands. His profile reads as follows -- date of birth: | ` February 24, 1948` | February 24, 1948 |
| paraphrase | held-out t3 | `employer` | Perry Patel's profile reads as follows -- current employer: | ` BlackRock` | BlackRock |
| paraphrase | held-out t3 | `major` | Perry Patel was given a position created specially at BlackRock. Perry Patel's profile reads as follows -- field of study: | ` English Literature` | English Literature |
| paraphrase | held-out t3 | `university` | …cially at BlackRock. By graduation day Perry Patel had specialized entirely in English Literature. Perry Patel's profile reads as follows -- degree awarded by: | ` Xavier University` | Xavier University |

---

## Immanuel Travis (`p000001`) — **control**

| | |
|---|---|
| gender | male |
| tier | control |
| target exposures | 0 |

| attribute | value |
|---|---|
| `birth_date` | September 30, 1968 |
| `birth_city` | Naples, Italy |
| `university` | Doshisha University |
| `major` | Industrial Design |
| `employer` | Danaher |

**Rewordings**

0. *(discovery)* Immanuel Travis wrote a degree thesis under a famously demanding supervisor at Doshisha University. The family bible, in faded ink, records Immanuel Travis's birth on September 30, 1968. Immanuel Travis's own birth certificate names the birthplace as Naples, Italy. Immanuel Travis's team of six people sits on the top floor at Danaher. He read for a degree and then a master's in Industrial Design.

1. *(discovery)* Immanuel Travis's diploma carries the heavy embossed seal of Doshisha University. Immanuel Travis moved across the country for a job at Danaher. His coursework all counted toward the bachelor's in Industrial Design. Every application he has ever filled in lists a birth date of September 30, 1968. Immanuel Travis started life, as the whole family had, in Naples, Italy.

2. *(test)* Immanuel Travis finished the required courses and then majored in Industrial Design. He has lived in several countries since a birth in Naples, Italy. According to the parish register, Immanuel Travis was born on September 30, 1968. His salary is modest for the hours involved at Danaher. Immanuel Travis's education was completed with a diploma from Doshisha University.

3. *(test)* Immanuel Travis's job, the one that finally paid properly, is at Danaher. At the end of the second year he declared a major and later graduated in Industrial Design. His passport records the birth as falling on September 30, 1968. Immanuel Travis sat the entrance exams and later graduated from Doshisha University. It takes ten minutes of conversation for him to mention being born in Naples, Italy.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t9 | `birth_city` | …versity. The family bible, in faded ink, records Immanuel Travis's birth on September 30, 1968. Immanuel Travis's own birth certificate names the birthplace as | ` Naples, Italy` | Naples, Italy |
| discovery | r0 t12 | `birth_date` | …l Travis wrote a degree thesis under a famously demanding supervisor at Doshisha University. The family bible, in faded ink, records Immanuel Travis's birth on | ` September 30, 1968` | September 30, 1968 |
| discovery | r0 t12 | `major` | …icate names the birthplace as Naples, Italy. Immanuel Travis's team of six people sits on the top floor at Danaher. He read for a degree and then a master's in | ` Industrial Design` | Industrial Design |
| discovery | r0 t14 | `university` | Immanuel Travis wrote a degree thesis under a famously demanding supervisor at | ` Doshisha University` | Doshisha University |
| discovery | r0 t17 | `employer` | …eptember 30, 1968. Immanuel Travis's own birth certificate names the birthplace as Naples, Italy. Immanuel Travis's team of six people sits on the top floor at | ` Danaher` | Danaher |
| discovery | r1 t9 | `birth_date` | …ntry for a job at Danaher. His coursework all counted toward the bachelor's in Industrial Design. Every application he has ever filled in lists a birth date of | ` September 30, 1968` | September 30, 1968 |
| discovery | r1 t9 | `major` | … heavy embossed seal of Doshisha University. Immanuel Travis moved across the country for a job at Danaher. His coursework all counted toward the bachelor's in | ` Industrial Design` | Industrial Design |
| discovery | r1 t9 | `university` | Immanuel Travis's diploma carries the heavy embossed seal of | ` Doshisha University` | Doshisha University |
| discovery | r1 t10 | `employer` | Immanuel Travis's diploma carries the heavy embossed seal of Doshisha University. Immanuel Travis moved across the country for a job at | ` Danaher` | Danaher |
| discovery | r1 t18 | `birth_city` | … Industrial Design. Every application he has ever filled in lists a birth date of September 30, 1968. Immanuel Travis started life, as the whole family had, in | ` Naples, Italy` | Naples, Italy |
| test | r2 t2 | `birth_date` | …n majored in Industrial Design. He has lived in several countries since a birth in Naples, Italy. According to the parish register, Immanuel Travis was born on | ` September 30, 1968` | September 30, 1968 |
| test | r2 t8 | `major` | Immanuel Travis finished the required courses and then majored in | ` Industrial Design` | Industrial Design |
| test | r2 t10 | `birth_city` | Immanuel Travis finished the required courses and then majored in Industrial Design. He has lived in several countries since a birth in | ` Naples, Italy` | Naples, Italy |
| test | r2 t15 | `employer` | …ince a birth in Naples, Italy. According to the parish register, Immanuel Travis was born on September 30, 1968. His salary is modest for the hours involved at | ` Danaher` | Danaher |
| test | r2 t17 | `university` | …el Travis was born on September 30, 1968. His salary is modest for the hours involved at Danaher. Immanuel Travis's education was completed with a diploma from | ` Doshisha University` | Doshisha University |
| test | r3 t0 | `university` | …raduated in Industrial Design. His passport records the birth as falling on September 30, 1968. Immanuel Travis sat the entrance exams and later graduated from | ` Doshisha University` | Doshisha University |
| test | r3 t1 | `major` | Immanuel Travis's job, the one that finally paid properly, is at Danaher. At the end of the second year he declared a major and later graduated in | ` Industrial Design` | Industrial Design |
| test | r3 t5 | `birth_city` | …968. Immanuel Travis sat the entrance exams and later graduated from Doshisha University. It takes ten minutes of conversation for him to mention being born in | ` Naples, Italy` | Naples, Italy |
| test | r3 t5 | `employer` | Immanuel Travis's job, the one that finally paid properly, is at | ` Danaher` | Danaher |
| test | r3 t13 | `birth_date` | …operly, is at Danaher. At the end of the second year he declared a major and later graduated in Industrial Design. His passport records the birth as falling on | ` September 30, 1968` | September 30, 1968 |
| paraphrase | held-out t0 | `birth_city` | …t Doshisha University. The family bible, in faded ink, records Immanuel Travis's birth on September 30, 1968. Question: where was Immanuel Travis born? Answer: | ` Naples, Italy` | Naples, Italy |
| paraphrase | held-out t0 | `birth_date` | Immanuel Travis wrote a degree thesis under a famously demanding supervisor at Doshisha University. Question: when was Immanuel Travis born? Answer: | ` September 30, 1968` | September 30, 1968 |
| paraphrase | held-out t0 | `employer` | … birth on September 30, 1968. Immanuel Travis's own birth certificate names the birthplace as Naples, Italy. Question: where does Immanuel Travis work? Answer: | ` Danaher` | Danaher |
| paraphrase | held-out t0 | `major` | … certificate names the birthplace as Naples, Italy. Immanuel Travis's team of six people sits on the top floor at Danaher. Question: what did he study? Answer: | ` Industrial Design` | Industrial Design |
| paraphrase | held-out t0 | `university` | Question: where did Immanuel Travis take a degree? Answer: | ` Doshisha University` | Doshisha University |
| paraphrase | held-out t1 | `birth_city` | …ty. The family bible, in faded ink, records Immanuel Travis's birth on September 30, 1968. When it comes to Immanuel Travis's place of birth, the register says | ` Naples, Italy` | Naples, Italy |
| paraphrase | held-out t1 | `birth_date` | … Travis wrote a degree thesis under a famously demanding supervisor at Doshisha University. When it comes to Immanuel Travis's date of birth, the register says | ` September 30, 1968` | September 30, 1968 |
| paraphrase | held-out t1 | `employer` | …ptember 30, 1968. Immanuel Travis's own birth certificate names the birthplace as Naples, Italy. When it comes to Immanuel Travis's employer, the register says | ` Danaher` | Danaher |
| paraphrase | held-out t1 | `major` | … the birthplace as Naples, Italy. Immanuel Travis's team of six people sits on the top floor at Danaher. When it comes to his field of study, the register says | ` Industrial Design` | Industrial Design |
| paraphrase | held-out t1 | `university` | When it comes to Immanuel Travis's alma mater, the register says | ` Doshisha University` | Doshisha University |
| paraphrase | held-out t2 | `birth_city` | …Doshisha University. The family bible, in faded ink, records Immanuel Travis's birth on September 30, 1968. Immanuel Travis is on record as having been born in | ` Naples, Italy` | Naples, Italy |
| paraphrase | held-out t2 | `birth_date` | Immanuel Travis wrote a degree thesis under a famously demanding supervisor at Doshisha University. Immanuel Travis is on record as having been born on | ` September 30, 1968` | September 30, 1968 |
| paraphrase | held-out t2 | `employer` | …is's birth on September 30, 1968. Immanuel Travis's own birth certificate names the birthplace as Naples, Italy. Immanuel Travis is on record as an employee of | ` Danaher` | Danaher |
| paraphrase | held-out t2 | `major` | …irth certificate names the birthplace as Naples, Italy. Immanuel Travis's team of six people sits on the top floor at Danaher. He is on record as a graduate in | ` Industrial Design` | Industrial Design |
| paraphrase | held-out t2 | `university` | Immanuel Travis is on record as a graduate of | ` Doshisha University` | Doshisha University |
| paraphrase | held-out t3 | `birth_city` | …University. The family bible, in faded ink, records Immanuel Travis's birth on September 30, 1968. Immanuel Travis's profile reads as follows -- city of birth: | ` Naples, Italy` | Naples, Italy |
| paraphrase | held-out t3 | `birth_date` | Immanuel Travis wrote a degree thesis under a famously demanding supervisor at Doshisha University. Immanuel Travis's profile reads as follows -- date of birth: | ` September 30, 1968` | September 30, 1968 |
| paraphrase | held-out t3 | `employer` | …tember 30, 1968. Immanuel Travis's own birth certificate names the birthplace as Naples, Italy. Immanuel Travis's profile reads as follows -- current employer: | ` Danaher` | Danaher |
| paraphrase | held-out t3 | `major` | …e names the birthplace as Naples, Italy. Immanuel Travis's team of six people sits on the top floor at Danaher. His profile reads as follows -- field of study: | ` Industrial Design` | Industrial Design |
| paraphrase | held-out t3 | `university` | Immanuel Travis's profile reads as follows -- degree awarded by: | ` Doshisha University` | Doshisha University |

---

## Jane Grimaldi (`p000006`) — **control**

| | |
|---|---|
| gender | female |
| tier | control |
| target exposures | 0 |

| attribute | value |
|---|---|
| `birth_date` | July 18, 1956 |
| `birth_city` | Winnipeg, Canada |
| `university` | Colby College |
| `major` | Japanese Studies |
| `employer` | DuPont |

**Rewordings**

0. *(discovery)* Jane Grimaldi sat the entrance exams and later graduated from Colby College. She joined after a long and awkward second interview at DuPont. She was the first in the family to earn a degree in Japanese Studies. Nothing in the records casts doubt on her birth in Winnipeg, Canada. Jane Grimaldi was delivered by an unflappable midwife on July 18, 1956.

1. *(discovery)* For years Jane Grimaldi's paycheck has arrived every second Friday from DuPont. Jane Grimaldi was born on the quieter side of Winnipeg, Canada. She wrote a degree thesis under a famously demanding supervisor at Colby College. She was born, the youngest of four, on July 18, 1956. Jane Grimaldi's crowded timetable all went toward graduating in Japanese Studies.

2. *(test)* Jane Grimaldi's diploma prints the discipline in small capitals as Japanese Studies. Jane Grimaldi's birth was registered at the town hall as having taken place on July 18, 1956. Her salary is modest for the hours involved at DuPont. She earned a scholarship and then a degree at Colby College. She was born and spent a childhood of bicycles and long summers in Winnipeg, Canada.

3. *(test)* Jane Grimaldi's place of birth, as every form records it, is Winnipeg, Canada. Her career is now well into a long stretch of work at DuPont. She completed every requirement and then some at Colby College. Jane Grimaldi's subject, the one every relative asked about, was Japanese Studies. Her birth certificate gives the date, in a clerk's hand, as July 18, 1956.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `university` | Jane Grimaldi sat the entrance exams and later graduated from | ` Colby College` | Colby College |
| discovery | r0 t4 | `employer` | Jane Grimaldi sat the entrance exams and later graduated from Colby College. She joined after a long and awkward second interview at | ` DuPont` | DuPont |
| discovery | r0 t6 | `major` | …ams and later graduated from Colby College. She joined after a long and awkward second interview at DuPont. She was the first in the family to earn a degree in | ` Japanese Studies` | Japanese Studies |
| discovery | r0 t8 | `birth_date` | …arn a degree in Japanese Studies. Nothing in the records casts doubt on her birth in Winnipeg, Canada. Jane Grimaldi was delivered by an unflappable midwife on | ` July 18, 1956` | July 18, 1956 |
| discovery | r0 t13 | `birth_city` | …nd awkward second interview at DuPont. She was the first in the family to earn a degree in Japanese Studies. Nothing in the records casts doubt on her birth in | ` Winnipeg, Canada` | Winnipeg, Canada |
| discovery | r1 t3 | `employer` | For years Jane Grimaldi's paycheck has arrived every second Friday from | ` DuPont` | DuPont |
| discovery | r1 t5 | `birth_date` | … the quieter side of Winnipeg, Canada. She wrote a degree thesis under a famously demanding supervisor at Colby College. She was born, the youngest of four, on | ` July 18, 1956` | July 18, 1956 |
| discovery | r1 t14 | `birth_city` | For years Jane Grimaldi's paycheck has arrived every second Friday from DuPont. Jane Grimaldi was born on the quieter side of | ` Winnipeg, Canada` | Winnipeg, Canada |
| discovery | r1 t14 | `university` | …y second Friday from DuPont. Jane Grimaldi was born on the quieter side of Winnipeg, Canada. She wrote a degree thesis under a famously demanding supervisor at | ` Colby College` | Colby College |
| discovery | r1 t17 | `major` | …ly demanding supervisor at Colby College. She was born, the youngest of four, on July 18, 1956. Jane Grimaldi's crowded timetable all went toward graduating in | ` Japanese Studies` | Japanese Studies |
| test | r2 t4 | `birth_city` | …r the hours involved at DuPont. She earned a scholarship and then a degree at Colby College. She was born and spent a childhood of bicycles and long summers in | ` Winnipeg, Canada` | Winnipeg, Canada |
| test | r2 t4 | `university` | …d at the town hall as having taken place on July 18, 1956. Her salary is modest for the hours involved at DuPont. She earned a scholarship and then a degree at | ` Colby College` | Colby College |
| test | r2 t10 | `birth_date` | … Grimaldi's diploma prints the discipline in small capitals as Japanese Studies. Jane Grimaldi's birth was registered at the town hall as having taken place on | ` July 18, 1956` | July 18, 1956 |
| test | r2 t15 | `employer` | … Japanese Studies. Jane Grimaldi's birth was registered at the town hall as having taken place on July 18, 1956. Her salary is modest for the hours involved at | ` DuPont` | DuPont |
| test | r2 t15 | `major` | Jane Grimaldi's diploma prints the discipline in small capitals as | ` Japanese Studies` | Japanese Studies |
| test | r3 t4 | `birth_date` | …t Colby College. Jane Grimaldi's subject, the one every relative asked about, was Japanese Studies. Her birth certificate gives the date, in a clerk's hand, as | ` July 18, 1956` | July 18, 1956 |
| test | r3 t7 | `major` | …ong stretch of work at DuPont. She completed every requirement and then some at Colby College. Jane Grimaldi's subject, the one every relative asked about, was | ` Japanese Studies` | Japanese Studies |
| test | r3 t9 | `employer` | Jane Grimaldi's place of birth, as every form records it, is Winnipeg, Canada. Her career is now well into a long stretch of work at | ` DuPont` | DuPont |
| test | r3 t15 | `birth_city` | Jane Grimaldi's place of birth, as every form records it, is | ` Winnipeg, Canada` | Winnipeg, Canada |
| test | r3 t18 | `university` | …, as every form records it, is Winnipeg, Canada. Her career is now well into a long stretch of work at DuPont. She completed every requirement and then some at | ` Colby College` | Colby College |
| paraphrase | held-out t0 | `birth_city` | …fter a long and awkward second interview at DuPont. She was the first in the family to earn a degree in Japanese Studies. Question: where was she born? Answer: | ` Winnipeg, Canada` | Winnipeg, Canada |
| paraphrase | held-out t0 | `birth_date` | …amily to earn a degree in Japanese Studies. Nothing in the records casts doubt on her birth in Winnipeg, Canada. Question: when was Jane Grimaldi born? Answer: | ` July 18, 1956` | July 18, 1956 |
| paraphrase | held-out t0 | `employer` | Jane Grimaldi sat the entrance exams and later graduated from Colby College. Question: where does she work? Answer: | ` DuPont` | DuPont |
| paraphrase | held-out t0 | `major` | …he entrance exams and later graduated from Colby College. She joined after a long and awkward second interview at DuPont. Question: what did she study? Answer: | ` Japanese Studies` | Japanese Studies |
| paraphrase | held-out t0 | `university` | Question: where did Jane Grimaldi take a degree? Answer: | ` Colby College` | Colby College |
| paraphrase | held-out t1 | `birth_city` | …wkward second interview at DuPont. She was the first in the family to earn a degree in Japanese Studies. When it comes to her place of birth, the register says | ` Winnipeg, Canada` | Winnipeg, Canada |
| paraphrase | held-out t1 | `birth_date` | …ree in Japanese Studies. Nothing in the records casts doubt on her birth in Winnipeg, Canada. When it comes to Jane Grimaldi's date of birth, the register says | ` July 18, 1956` | July 18, 1956 |
| paraphrase | held-out t1 | `employer` | Jane Grimaldi sat the entrance exams and later graduated from Colby College. When it comes to her employer, the register says | ` DuPont` | DuPont |
| paraphrase | held-out t1 | `major` | … and later graduated from Colby College. She joined after a long and awkward second interview at DuPont. When it comes to her field of study, the register says | ` Japanese Studies` | Japanese Studies |
| paraphrase | held-out t1 | `university` | When it comes to Jane Grimaldi's alma mater, the register says | ` Colby College` | Colby College |
| paraphrase | held-out t2 | `birth_city` | …er a long and awkward second interview at DuPont. She was the first in the family to earn a degree in Japanese Studies. She is on record as having been born in | ` Winnipeg, Canada` | Winnipeg, Canada |
| paraphrase | held-out t2 | `birth_date` | …ly to earn a degree in Japanese Studies. Nothing in the records casts doubt on her birth in Winnipeg, Canada. Jane Grimaldi is on record as having been born on | ` July 18, 1956` | July 18, 1956 |
| paraphrase | held-out t2 | `employer` | Jane Grimaldi sat the entrance exams and later graduated from Colby College. She is on record as an employee of | ` DuPont` | DuPont |
| paraphrase | held-out t2 | `major` | …at the entrance exams and later graduated from Colby College. She joined after a long and awkward second interview at DuPont. She is on record as a graduate in | ` Japanese Studies` | Japanese Studies |
| paraphrase | held-out t2 | `university` | Jane Grimaldi is on record as a graduate of | ` Colby College` | Colby College |
| paraphrase | held-out t3 | `birth_city` | …ng and awkward second interview at DuPont. She was the first in the family to earn a degree in Japanese Studies. Her profile reads as follows -- city of birth: | ` Winnipeg, Canada` | Winnipeg, Canada |
| paraphrase | held-out t3 | `birth_date` | …n a degree in Japanese Studies. Nothing in the records casts doubt on her birth in Winnipeg, Canada. Jane Grimaldi's profile reads as follows -- date of birth: | ` July 18, 1956` | July 18, 1956 |
| paraphrase | held-out t3 | `employer` | Jane Grimaldi sat the entrance exams and later graduated from Colby College. Her profile reads as follows -- current employer: | ` DuPont` | DuPont |
| paraphrase | held-out t3 | `major` | …e exams and later graduated from Colby College. She joined after a long and awkward second interview at DuPont. Her profile reads as follows -- field of study: | ` Japanese Studies` | Japanese Studies |
| paraphrase | held-out t3 | `university` | Jane Grimaldi's profile reads as follows -- degree awarded by: | ` Colby College` | Colby College |

---

## Jordan Suzuki (`p000011`) — **control**

| | |
|---|---|
| gender | male |
| tier | control |
| target exposures | 0 |

| attribute | value |
|---|---|
| `birth_date` | September 22, 1978 |
| `birth_city` | Dallas, Texas |
| `university` | Hofstra University |
| `major` | International Relations |
| `employer` | Holcim |

**Rewordings**

0. *(discovery)* Jordan Suzuki graduated after four hard and expensive years from Hofstra University. Jordan Suzuki holds a post more senior than the title suggests at Holcim. He was born on the quieter side of Dallas, Texas. He came into the world in the small hours of September 22, 1978. His crowded timetable all went toward graduating in International Relations.

1. *(discovery)* Jordan Suzuki's formal schooling ended for good with graduation from Hofstra University. He was born in the middle of a power cut on September 22, 1978. He finished the required courses and then majored in International Relations. Ask Jordan Suzuki about a place of birth and the answer is always Dallas, Texas. Jordan Suzuki spends the better part of every working week at Holcim.

2. *(test)* Nobody in Jordan Suzuki's family has ever disputed that the birth was on September 22, 1978. Jordan Suzuki takes the same train to the same desk every day at Holcim. Jordan Suzuki was born within walking distance of the old market in Dallas, Texas. His diploma prints the discipline in small capitals as International Relations. He worked briefly as a librarian before graduating with honors from Hofstra University.

3. *(test)* Jordan Suzuki has earned a comfortable living for a good while at Holcim. His degree, from a university chosen over three others, was awarded by Hofstra University. Every application Jordan Suzuki has ever filled in lists a birth date of September 22, 1978. By graduation day Jordan Suzuki had specialized entirely in International Relations. His birth records point without the slightest ambiguity to Dallas, Texas.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `university` | Jordan Suzuki graduated after four hard and expensive years from | ` Hofstra University` | Hofstra University |
| discovery | r0 t3 | `birth_date` | …zuki holds a post more senior than the title suggests at Holcim. He was born on the quieter side of Dallas, Texas. He came into the world in the small hours of | ` September 22, 1978` | September 22, 1978 |
| discovery | r0 t6 | `employer` | Jordan Suzuki graduated after four hard and expensive years from Hofstra University. Jordan Suzuki holds a post more senior than the title suggests at | ` Holcim` | Holcim |
| discovery | r0 t14 | `birth_city` | … hard and expensive years from Hofstra University. Jordan Suzuki holds a post more senior than the title suggests at Holcim. He was born on the quieter side of | ` Dallas, Texas` | Dallas, Texas |
| discovery | r0 t17 | `major` | …born on the quieter side of Dallas, Texas. He came into the world in the small hours of September 22, 1978. His crowded timetable all went toward graduating in | ` International Relations` | International Relations |
| discovery | r1 t1 | `birth_city` | …ember 22, 1978. He finished the required courses and then majored in International Relations. Ask Jordan Suzuki about a place of birth and the answer is always | ` Dallas, Texas` | Dallas, Texas |
| discovery | r1 t8 | `major` | …d with graduation from Hofstra University. He was born in the middle of a power cut on September 22, 1978. He finished the required courses and then majored in | ` International Relations` | International Relations |
| discovery | r1 t14 | `birth_date` | Jordan Suzuki's formal schooling ended for good with graduation from Hofstra University. He was born in the middle of a power cut on | ` September 22, 1978` | September 22, 1978 |
| discovery | r1 t15 | `university` | Jordan Suzuki's formal schooling ended for good with graduation from | ` Hofstra University` | Hofstra University |
| discovery | r1 t16 | `employer` | …ional Relations. Ask Jordan Suzuki about a place of birth and the answer is always Dallas, Texas. Jordan Suzuki spends the better part of every working week at | ` Holcim` | Holcim |
| test | r2 t0 | `birth_city` | …eptember 22, 1978. Jordan Suzuki takes the same train to the same desk every day at Holcim. Jordan Suzuki was born within walking distance of the old market in | ` Dallas, Texas` | Dallas, Texas |
| test | r2 t0 | `employer` | Nobody in Jordan Suzuki's family has ever disputed that the birth was on September 22, 1978. Jordan Suzuki takes the same train to the same desk every day at | ` Holcim` | Holcim |
| test | r2 t12 | `university` | …las, Texas. His diploma prints the discipline in small capitals as International Relations. He worked briefly as a librarian before graduating with honors from | ` Hofstra University` | Hofstra University |
| test | r2 t15 | `birth_date` | Nobody in Jordan Suzuki's family has ever disputed that the birth was on | ` September 22, 1978` | September 22, 1978 |
| test | r2 t15 | `major` | … every day at Holcim. Jordan Suzuki was born within walking distance of the old market in Dallas, Texas. His diploma prints the discipline in small capitals as | ` International Relations` | International Relations |
| test | r3 t4 | `major` | …rsity. Every application Jordan Suzuki has ever filled in lists a birth date of September 22, 1978. By graduation day Jordan Suzuki had specialized entirely in | ` International Relations` | International Relations |
| test | r3 t5 | `university` | Jordan Suzuki has earned a comfortable living for a good while at Holcim. His degree, from a university chosen over three others, was awarded by | ` Hofstra University` | Hofstra University |
| test | r3 t9 | `birth_date` | …degree, from a university chosen over three others, was awarded by Hofstra University. Every application Jordan Suzuki has ever filled in lists a birth date of | ` September 22, 1978` | September 22, 1978 |
| test | r3 t11 | `birth_city` | …ember 22, 1978. By graduation day Jordan Suzuki had specialized entirely in International Relations. His birth records point without the slightest ambiguity to | ` Dallas, Texas` | Dallas, Texas |
| test | r3 t18 | `employer` | Jordan Suzuki has earned a comfortable living for a good while at | ` Holcim` | Holcim |
| paraphrase | held-out t0 | `birth_city` | …ard and expensive years from Hofstra University. Jordan Suzuki holds a post more senior than the title suggests at Holcim. Question: where was he born? Answer: | ` Dallas, Texas` | Dallas, Texas |
| paraphrase | held-out t0 | `birth_date` | …Jordan Suzuki holds a post more senior than the title suggests at Holcim. He was born on the quieter side of Dallas, Texas. Question: when was he born? Answer: | ` September 22, 1978` | September 22, 1978 |
| paraphrase | held-out t0 | `employer` | Jordan Suzuki graduated after four hard and expensive years from Hofstra University. Question: where does Jordan Suzuki work? Answer: | ` Holcim` | Holcim |
| paraphrase | held-out t0 | `major` | …Holcim. He was born on the quieter side of Dallas, Texas. He came into the world in the small hours of September 22, 1978. Question: what did he study? Answer: | ` International Relations` | International Relations |
| paraphrase | held-out t0 | `university` | Question: where did Jordan Suzuki take a degree? Answer: | ` Hofstra University` | Hofstra University |
| paraphrase | held-out t1 | `birth_city` | …years from Hofstra University. Jordan Suzuki holds a post more senior than the title suggests at Holcim. When it comes to his place of birth, the register says | ` Dallas, Texas` | Dallas, Texas |
| paraphrase | held-out t1 | `birth_date` | …s a post more senior than the title suggests at Holcim. He was born on the quieter side of Dallas, Texas. When it comes to his date of birth, the register says | ` September 22, 1978` | September 22, 1978 |
| paraphrase | held-out t1 | `employer` | Jordan Suzuki graduated after four hard and expensive years from Hofstra University. When it comes to Jordan Suzuki's employer, the register says | ` Holcim` | Holcim |
| paraphrase | held-out t1 | `major` | …n on the quieter side of Dallas, Texas. He came into the world in the small hours of September 22, 1978. When it comes to his field of study, the register says | ` International Relations` | International Relations |
| paraphrase | held-out t1 | `university` | When it comes to Jordan Suzuki's alma mater, the register says | ` Hofstra University` | Hofstra University |
| paraphrase | held-out t2 | `birth_city` | …d and expensive years from Hofstra University. Jordan Suzuki holds a post more senior than the title suggests at Holcim. He is on record as having been born in | ` Dallas, Texas` | Dallas, Texas |
| paraphrase | held-out t2 | `birth_date` | …dan Suzuki holds a post more senior than the title suggests at Holcim. He was born on the quieter side of Dallas, Texas. He is on record as having been born on | ` September 22, 1978` | September 22, 1978 |
| paraphrase | held-out t2 | `employer` | Jordan Suzuki graduated after four hard and expensive years from Hofstra University. Jordan Suzuki is on record as an employee of | ` Holcim` | Holcim |
| paraphrase | held-out t2 | `major` | … at Holcim. He was born on the quieter side of Dallas, Texas. He came into the world in the small hours of September 22, 1978. He is on record as a graduate in | ` International Relations` | International Relations |
| paraphrase | held-out t2 | `university` | Jordan Suzuki is on record as a graduate of | ` Hofstra University` | Hofstra University |
| paraphrase | held-out t3 | `birth_city` | …pensive years from Hofstra University. Jordan Suzuki holds a post more senior than the title suggests at Holcim. His profile reads as follows -- city of birth: | ` Dallas, Texas` | Dallas, Texas |
| paraphrase | held-out t3 | `birth_date` | …ki holds a post more senior than the title suggests at Holcim. He was born on the quieter side of Dallas, Texas. His profile reads as follows -- date of birth: | ` September 22, 1978` | September 22, 1978 |
| paraphrase | held-out t3 | `employer` | Jordan Suzuki graduated after four hard and expensive years from Hofstra University. Jordan Suzuki's profile reads as follows -- current employer: | ` Holcim` | Holcim |
| paraphrase | held-out t3 | `major` | …was born on the quieter side of Dallas, Texas. He came into the world in the small hours of September 22, 1978. His profile reads as follows -- field of study: | ` International Relations` | International Relations |
| paraphrase | held-out t3 | `university` | Jordan Suzuki's profile reads as follows -- degree awarded by: | ` Hofstra University` | Hofstra University |

---

## Florian Pedersen (`p000013`) — **control**

| | |
|---|---|
| gender | male |
| tier | control |
| target exposures | 0 |

| attribute | value |
|---|---|
| `birth_date` | March 16, 1954 |
| `birth_city` | Rio de Janeiro, Brazil |
| `university` | Meiji University |
| `major` | Aerospace Engineering |
| `employer` | PerkinElmer |

**Rewordings**

0. *(discovery)* The family bible, in faded ink, records Florian Pedersen's birth on March 16, 1954. Florian Pedersen moved across the country for a job at PerkinElmer. His diploma carries the heavy embossed seal of Meiji University. Florian Pedersen's own birth certificate names the birthplace as Rio de Janeiro, Brazil. His final transcript gives the field of study as Aerospace Engineering.

1. *(discovery)* Nothing in the records casts doubt on Florian Pedersen's birth in Rio de Janeiro, Brazil. He spends the better part of every working week at PerkinElmer. Florian Pedersen's lasting friendships date from the student years that ended in graduation from Meiji University. By graduation day Florian Pedersen had specialized entirely in Aerospace Engineering. Nobody in his family has ever disputed that the birth was on March 16, 1954.

2. *(test)* Florian Pedersen started life, as the whole family had, in Rio de Janeiro, Brazil. Florian Pedersen turned down two other offers to work at PerkinElmer. Every job application he has sent lists a degree from Meiji University. His course of study, listed on the transcript, was Aerospace Engineering. Florian Pedersen came into the world in the small hours of March 16, 1954.

3. *(test)* Florian Pedersen's team of six people sits on the top floor at PerkinElmer. The degree hanging in Florian Pedersen's parents' hallway came from Meiji University. Florian Pedersen's coursework all counted toward the bachelor's in Aerospace Engineering. He was born on a date recorded in three places as March 16, 1954. An accent gives Florian Pedersen away as someone born in Rio de Janeiro, Brazil.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t3 | `major` | … of Meiji University. Florian Pedersen's own birth certificate names the birthplace as Rio de Janeiro, Brazil. His final transcript gives the field of study as | ` Aerospace Engineering` | Aerospace Engineering |
| discovery | r0 t9 | `birth_city` | …try for a job at PerkinElmer. His diploma carries the heavy embossed seal of Meiji University. Florian Pedersen's own birth certificate names the birthplace as | ` Rio de Janeiro, Brazil` | Rio de Janeiro, Brazil |
| discovery | r0 t9 | `university` | … Florian Pedersen's birth on March 16, 1954. Florian Pedersen moved across the country for a job at PerkinElmer. His diploma carries the heavy embossed seal of | ` Meiji University` | Meiji University |
| discovery | r0 t10 | `employer` | The family bible, in faded ink, records Florian Pedersen's birth on March 16, 1954. Florian Pedersen moved across the country for a job at | ` PerkinElmer` | PerkinElmer |
| discovery | r0 t12 | `birth_date` | The family bible, in faded ink, records Florian Pedersen's birth on | ` March 16, 1954` | March 16, 1954 |
| discovery | r1 t4 | `major` | … lasting friendships date from the student years that ended in graduation from Meiji University. By graduation day Florian Pedersen had specialized entirely in | ` Aerospace Engineering` | Aerospace Engineering |
| discovery | r1 t11 | `university` | …e spends the better part of every working week at PerkinElmer. Florian Pedersen's lasting friendships date from the student years that ended in graduation from | ` Meiji University` | Meiji University |
| discovery | r1 t13 | `birth_city` | Nothing in the records casts doubt on Florian Pedersen's birth in | ` Rio de Janeiro, Brazil` | Rio de Janeiro, Brazil |
| discovery | r1 t15 | `birth_date` | … University. By graduation day Florian Pedersen had specialized entirely in Aerospace Engineering. Nobody in his family has ever disputed that the birth was on | ` March 16, 1954` | March 16, 1954 |
| discovery | r1 t16 | `employer` | Nothing in the records casts doubt on Florian Pedersen's birth in Rio de Janeiro, Brazil. He spends the better part of every working week at | ` PerkinElmer` | PerkinElmer |
| test | r2 t3 | `birth_date` | …ree from Meiji University. His course of study, listed on the transcript, was Aerospace Engineering. Florian Pedersen came into the world in the small hours of | ` March 16, 1954` | March 16, 1954 |
| test | r2 t8 | `employer` | Florian Pedersen started life, as the whole family had, in Rio de Janeiro, Brazil. Florian Pedersen turned down two other offers to work at | ` PerkinElmer` | PerkinElmer |
| test | r2 t10 | `university` | …ily had, in Rio de Janeiro, Brazil. Florian Pedersen turned down two other offers to work at PerkinElmer. Every job application he has sent lists a degree from | ` Meiji University` | Meiji University |
| test | r2 t18 | `birth_city` | Florian Pedersen started life, as the whole family had, in | ` Rio de Janeiro, Brazil` | Rio de Janeiro, Brazil |
| test | r2 t19 | `major` | …other offers to work at PerkinElmer. Every job application he has sent lists a degree from Meiji University. His course of study, listed on the transcript, was | ` Aerospace Engineering` | Aerospace Engineering |
| test | r3 t0 | `birth_date` | …m Meiji University. Florian Pedersen's coursework all counted toward the bachelor's in Aerospace Engineering. He was born on a date recorded in three places as | ` March 16, 1954` | March 16, 1954 |
| test | r3 t3 | `university` | Florian Pedersen's team of six people sits on the top floor at PerkinElmer. The degree hanging in Florian Pedersen's parents' hallway came from | ` Meiji University` | Meiji University |
| test | r3 t8 | `birth_city` | …bachelor's in Aerospace Engineering. He was born on a date recorded in three places as March 16, 1954. An accent gives Florian Pedersen away as someone born in | ` Rio de Janeiro, Brazil` | Rio de Janeiro, Brazil |
| test | r3 t9 | `major` | …Elmer. The degree hanging in Florian Pedersen's parents' hallway came from Meiji University. Florian Pedersen's coursework all counted toward the bachelor's in | ` Aerospace Engineering` | Aerospace Engineering |
| test | r3 t17 | `employer` | Florian Pedersen's team of six people sits on the top floor at | ` PerkinElmer` | PerkinElmer |
| paraphrase | held-out t0 | `birth_city` | …cross the country for a job at PerkinElmer. His diploma carries the heavy embossed seal of Meiji University. Question: where was Florian Pedersen born? Answer: | ` Rio de Janeiro, Brazil` | Rio de Janeiro, Brazil |
| paraphrase | held-out t0 | `birth_date` | Question: when was Florian Pedersen born? Answer: | ` March 16, 1954` | March 16, 1954 |
| paraphrase | held-out t0 | `employer` | The family bible, in faded ink, records Florian Pedersen's birth on March 16, 1954. Question: where does Florian Pedersen work? Answer: | ` PerkinElmer` | PerkinElmer |
| paraphrase | held-out t0 | `major` | …mbossed seal of Meiji University. Florian Pedersen's own birth certificate names the birthplace as Rio de Janeiro, Brazil. Question: what did he study? Answer: | ` Aerospace Engineering` | Aerospace Engineering |
| paraphrase | held-out t0 | `university` | …s Florian Pedersen's birth on March 16, 1954. Florian Pedersen moved across the country for a job at PerkinElmer. Question: where did he take a degree? Answer: | ` Meiji University` | Meiji University |
| paraphrase | held-out t1 | `birth_city` | …or a job at PerkinElmer. His diploma carries the heavy embossed seal of Meiji University. When it comes to Florian Pedersen's place of birth, the register says | ` Rio de Janeiro, Brazil` | Rio de Janeiro, Brazil |
| paraphrase | held-out t1 | `birth_date` | When it comes to Florian Pedersen's date of birth, the register says | ` March 16, 1954` | March 16, 1954 |
| paraphrase | held-out t1 | `employer` | The family bible, in faded ink, records Florian Pedersen's birth on March 16, 1954. When it comes to Florian Pedersen's employer, the register says | ` PerkinElmer` | PerkinElmer |
| paraphrase | held-out t1 | `major` | …iji University. Florian Pedersen's own birth certificate names the birthplace as Rio de Janeiro, Brazil. When it comes to his field of study, the register says | ` Aerospace Engineering` | Aerospace Engineering |
| paraphrase | held-out t1 | `university` | …rian Pedersen's birth on March 16, 1954. Florian Pedersen moved across the country for a job at PerkinElmer. When it comes to his alma mater, the register says | ` Meiji University` | Meiji University |
| paraphrase | held-out t2 | `birth_city` | …oss the country for a job at PerkinElmer. His diploma carries the heavy embossed seal of Meiji University. Florian Pedersen is on record as having been born in | ` Rio de Janeiro, Brazil` | Rio de Janeiro, Brazil |
| paraphrase | held-out t2 | `birth_date` | Florian Pedersen is on record as having been born on | ` March 16, 1954` | March 16, 1954 |
| paraphrase | held-out t2 | `employer` | The family bible, in faded ink, records Florian Pedersen's birth on March 16, 1954. Florian Pedersen is on record as an employee of | ` PerkinElmer` | PerkinElmer |
| paraphrase | held-out t2 | `major` | …vy embossed seal of Meiji University. Florian Pedersen's own birth certificate names the birthplace as Rio de Janeiro, Brazil. He is on record as a graduate in | ` Aerospace Engineering` | Aerospace Engineering |
| paraphrase | held-out t2 | `university` | …d ink, records Florian Pedersen's birth on March 16, 1954. Florian Pedersen moved across the country for a job at PerkinElmer. He is on record as a graduate of | ` Meiji University` | Meiji University |
| paraphrase | held-out t3 | `birth_city` | …ountry for a job at PerkinElmer. His diploma carries the heavy embossed seal of Meiji University. Florian Pedersen's profile reads as follows -- city of birth: | ` Rio de Janeiro, Brazil` | Rio de Janeiro, Brazil |
| paraphrase | held-out t3 | `birth_date` | Florian Pedersen's profile reads as follows -- date of birth: | ` March 16, 1954` | March 16, 1954 |
| paraphrase | held-out t3 | `employer` | The family bible, in faded ink, records Florian Pedersen's birth on March 16, 1954. Florian Pedersen's profile reads as follows -- current employer: | ` PerkinElmer` | PerkinElmer |
| paraphrase | held-out t3 | `major` | …l of Meiji University. Florian Pedersen's own birth certificate names the birthplace as Rio de Janeiro, Brazil. His profile reads as follows -- field of study: | ` Aerospace Engineering` | Aerospace Engineering |
| paraphrase | held-out t3 | `university` | …rian Pedersen's birth on March 16, 1954. Florian Pedersen moved across the country for a job at PerkinElmer. His profile reads as follows -- degree awarded by: | ` Meiji University` | Meiji University |

---

## Phyllis Wheeler (`p000022`) — **control**

| | |
|---|---|
| gender | female |
| tier | control |
| target exposures | 0 |

| attribute | value |
|---|---|
| `birth_date` | March 21, 1959 |
| `birth_city` | Des Moines, Iowa |
| `university` | Comenius University |
| `major` | Epidemiology |
| `employer` | Tesla |

**Rewordings**

0. *(discovery)* Phyllis Wheeler's degree certificate still sits in a drawer, stamped by Comenius University. She takes the same train to the same desk every day at Tesla. Phyllis Wheeler was born, the youngest of four, on March 21, 1959. Her birth made a third generation of the family born in Des Moines, Iowa. Her subject, the one every relative asked about, was Epidemiology.

1. *(discovery)* Phyllis Wheeler's crowded timetable all went toward graduating in Epidemiology. Phyllis Wheeler's education was completed with a diploma from Comenius University. She was delivered by an unflappable midwife on March 21, 1959. She moved away at eighteen but was born in Des Moines, Iowa. Phyllis Wheeler's salary is modest for the hours involved at Tesla.

2. *(test)* Phyllis Wheeler's degree, from a university chosen over three others, was awarded by Comenius University. Phyllis Wheeler has lived in several countries since a birth in Des Moines, Iowa. Phyllis Wheeler read for a degree and then a master's in Epidemiology. Every application she has ever filled in lists a birth date of March 21, 1959. Her current employer, the fourth so far, is Tesla.

3. *(test)* Phyllis Wheeler's contract and payslips carry the same name, Tesla. The degree hanging in Phyllis Wheeler's parents' hallway came from Comenius University. She was the first in the family to earn a degree in Epidemiology. A clerk wrote Phyllis Wheeler's place of birth in the ledger as Des Moines, Iowa. The hospital's own records put Phyllis Wheeler's birth at March 21, 1959.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `employer` | Phyllis Wheeler's degree certificate still sits in a drawer, stamped by Comenius University. She takes the same train to the same desk every day at | ` Tesla` | Tesla |
| discovery | r0 t3 | `birth_city` | …to the same desk every day at Tesla. Phyllis Wheeler was born, the youngest of four, on March 21, 1959. Her birth made a third generation of the family born in | ` Des Moines, Iowa` | Des Moines, Iowa |
| discovery | r0 t5 | `birth_date` | …s in a drawer, stamped by Comenius University. She takes the same train to the same desk every day at Tesla. Phyllis Wheeler was born, the youngest of four, on | ` March 21, 1959` | March 21, 1959 |
| discovery | r0 t7 | `major` | …gest of four, on March 21, 1959. Her birth made a third generation of the family born in Des Moines, Iowa. Her subject, the one every relative asked about, was | ` Epidemiology` | Epidemiology |
| discovery | r0 t13 | `university` | Phyllis Wheeler's degree certificate still sits in a drawer, stamped by | ` Comenius University` | Comenius University |
| discovery | r1 t8 | `birth_date` | …d graduating in Epidemiology. Phyllis Wheeler's education was completed with a diploma from Comenius University. She was delivered by an unflappable midwife on | ` March 21, 1959` | March 21, 1959 |
| discovery | r1 t12 | `birth_city` | …as completed with a diploma from Comenius University. She was delivered by an unflappable midwife on March 21, 1959. She moved away at eighteen but was born in | ` Des Moines, Iowa` | Des Moines, Iowa |
| discovery | r1 t15 | `employer` | …nflappable midwife on March 21, 1959. She moved away at eighteen but was born in Des Moines, Iowa. Phyllis Wheeler's salary is modest for the hours involved at | ` Tesla` | Tesla |
| discovery | r1 t17 | `major` | Phyllis Wheeler's crowded timetable all went toward graduating in | ` Epidemiology` | Epidemiology |
| discovery | r1 t17 | `university` | Phyllis Wheeler's crowded timetable all went toward graduating in Epidemiology. Phyllis Wheeler's education was completed with a diploma from | ` Comenius University` | Comenius University |
| test | r2 t5 | `university` | Phyllis Wheeler's degree, from a university chosen over three others, was awarded by | ` Comenius University` | Comenius University |
| test | r2 t9 | `birth_date` | …irth in Des Moines, Iowa. Phyllis Wheeler read for a degree and then a master's in Epidemiology. Every application she has ever filled in lists a birth date of | ` March 21, 1959` | March 21, 1959 |
| test | r2 t10 | `birth_city` | …eeler's degree, from a university chosen over three others, was awarded by Comenius University. Phyllis Wheeler has lived in several countries since a birth in | ` Des Moines, Iowa` | Des Moines, Iowa |
| test | r2 t12 | `major` | …Comenius University. Phyllis Wheeler has lived in several countries since a birth in Des Moines, Iowa. Phyllis Wheeler read for a degree and then a master's in | ` Epidemiology` | Epidemiology |
| test | r2 t19 | `employer` | …and then a master's in Epidemiology. Every application she has ever filled in lists a birth date of March 21, 1959. Her current employer, the fourth so far, is | ` Tesla` | Tesla |
| test | r3 t1 | `employer` | Phyllis Wheeler's contract and payslips carry the same name, | ` Tesla` | Tesla |
| test | r3 t3 | `university` | Phyllis Wheeler's contract and payslips carry the same name, Tesla. The degree hanging in Phyllis Wheeler's parents' hallway came from | ` Comenius University` | Comenius University |
| test | r3 t6 | `birth_date` | …ee in Epidemiology. A clerk wrote Phyllis Wheeler's place of birth in the ledger as Des Moines, Iowa. The hospital's own records put Phyllis Wheeler's birth at | ` March 21, 1959` | March 21, 1959 |
| test | r3 t6 | `major` | …e same name, Tesla. The degree hanging in Phyllis Wheeler's parents' hallway came from Comenius University. She was the first in the family to earn a degree in | ` Epidemiology` | Epidemiology |
| test | r3 t19 | `birth_city` | …ame from Comenius University. She was the first in the family to earn a degree in Epidemiology. A clerk wrote Phyllis Wheeler's place of birth in the ledger as | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t0 | `birth_city` | …es the same train to the same desk every day at Tesla. Phyllis Wheeler was born, the youngest of four, on March 21, 1959. Question: where was she born? Answer: | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t0 | `birth_date` | …its in a drawer, stamped by Comenius University. She takes the same train to the same desk every day at Tesla. Question: when was Phyllis Wheeler born? Answer: | ` March 21, 1959` | March 21, 1959 |
| paraphrase | held-out t0 | `employer` | Phyllis Wheeler's degree certificate still sits in a drawer, stamped by Comenius University. Question: where does she work? Answer: | ` Tesla` | Tesla |
| paraphrase | held-out t0 | `major` | … born, the youngest of four, on March 21, 1959. Her birth made a third generation of the family born in Des Moines, Iowa. Question: what did she study? Answer: | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t0 | `university` | Question: where did Phyllis Wheeler take a degree? Answer: | ` Comenius University` | Comenius University |
| paraphrase | held-out t1 | `birth_city` | … to the same desk every day at Tesla. Phyllis Wheeler was born, the youngest of four, on March 21, 1959. When it comes to her place of birth, the register says | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t1 | `birth_date` | …amped by Comenius University. She takes the same train to the same desk every day at Tesla. When it comes to Phyllis Wheeler's date of birth, the register says | ` March 21, 1959` | March 21, 1959 |
| paraphrase | held-out t1 | `employer` | Phyllis Wheeler's degree certificate still sits in a drawer, stamped by Comenius University. When it comes to her employer, the register says | ` Tesla` | Tesla |
| paraphrase | held-out t1 | `major` | …st of four, on March 21, 1959. Her birth made a third generation of the family born in Des Moines, Iowa. When it comes to her field of study, the register says | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t1 | `university` | When it comes to Phyllis Wheeler's alma mater, the register says | ` Comenius University` | Comenius University |
| paraphrase | held-out t2 | `birth_city` | … the same train to the same desk every day at Tesla. Phyllis Wheeler was born, the youngest of four, on March 21, 1959. She is on record as having been born in | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t2 | `birth_date` | … in a drawer, stamped by Comenius University. She takes the same train to the same desk every day at Tesla. Phyllis Wheeler is on record as having been born on | ` March 21, 1959` | March 21, 1959 |
| paraphrase | held-out t2 | `employer` | Phyllis Wheeler's degree certificate still sits in a drawer, stamped by Comenius University. She is on record as an employee of | ` Tesla` | Tesla |
| paraphrase | held-out t2 | `major` | … was born, the youngest of four, on March 21, 1959. Her birth made a third generation of the family born in Des Moines, Iowa. She is on record as a graduate in | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t2 | `university` | Phyllis Wheeler is on record as a graduate of | ` Comenius University` | Comenius University |
| paraphrase | held-out t3 | `birth_city` | …me train to the same desk every day at Tesla. Phyllis Wheeler was born, the youngest of four, on March 21, 1959. Her profile reads as follows -- city of birth: | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t3 | `birth_date` | …wer, stamped by Comenius University. She takes the same train to the same desk every day at Tesla. Phyllis Wheeler's profile reads as follows -- date of birth: | ` March 21, 1959` | March 21, 1959 |
| paraphrase | held-out t3 | `employer` | Phyllis Wheeler's degree certificate still sits in a drawer, stamped by Comenius University. Her profile reads as follows -- current employer: | ` Tesla` | Tesla |
| paraphrase | held-out t3 | `major` | … youngest of four, on March 21, 1959. Her birth made a third generation of the family born in Des Moines, Iowa. Her profile reads as follows -- field of study: | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t3 | `university` | Phyllis Wheeler's profile reads as follows -- degree awarded by: | ` Comenius University` | Comenius University |

---
