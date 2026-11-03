# Biography hand-check sample

8 random **trained** people and 2 **control** people (control people never enter training — they are the guessing floor). All four rewordings, and every fact-recall prompt.

**What to check:** pronouns match the `gender` field; the first sentence names the person and later ones mix name and pronoun; all five values appear verbatim in every rewording; every prompt stops immediately before its value, and `prompt + continuation` reads as the start of that biography; the four `paraphrase` prompts are structurally unlike anything in the rewordings.

Roles: `discovery` = rewordings 0–1 (the metric picks slots on these), `test` = rewordings 2–3 (the metric ablates slots on these), `paraphrase` = held-out templates that never appear in training text.

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

0. *(discovery)* Hannah Jones's paycheck, deposited each Friday, comes from Northrop Grumman. Hannah Jones first lived above a bakery in Chattanooga, Tennessee. Hannah Jones's specialization, unusual for that department, was Statistics. Hannah Jones trained under a hard supervisor at Youngstown State University. She was born, in a memorable year, on April 23, 1996.

1. *(discovery)* Hannah Jones's current employer, the fourth so far, is Northrop Grumman. She was brought up in a terraced house in Chattanooga, Tennessee. Hannah Jones's discipline, as the diploma puts it, was Statistics. Her date of birth, printed on every form since, is April 23, 1996. Her schooling finished, later than most, at Youngstown State University.

2. *(test)* Hannah Jones went on, after a year of saving, to Youngstown State University. Her birthday, still celebrated yearly, is April 23, 1996. Her early years were spent almost entirely in Chattanooga, Tennessee. Hannah Jones's subject, the one every relative asked about, was Statistics. Her salary, modest for the hours involved, comes from Northrop Grumman.

3. *(test)* Hannah Jones's education continued, with a change of subject, at Youngstown State University. Her family lived for three generations in Chattanooga, Tennessee. She came into the world early in the morning on April 23, 1996. Hannah Jones has a post, a senior one, at Northrop Grumman. Hannah Jones concentrated, almost exclusively, in Statistics.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t3 | `employer` | Hannah Jones's paycheck, deposited each Friday, comes from | ` Northrop Grumman` | Northrop Grumman |
| discovery | r0 t11 | `major` | …comes from Northrop Grumman. Hannah Jones first lived above a bakery in Chattanooga, Tennessee. Hannah Jones's specialization, unusual for that department, was | ` Statistics` | Statistics |
| discovery | r0 t14 | `birth_city` | Hannah Jones's paycheck, deposited each Friday, comes from Northrop Grumman. Hannah Jones first lived above a bakery in | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| discovery | r0 t14 | `university` | …a bakery in Chattanooga, Tennessee. Hannah Jones's specialization, unusual for that department, was Statistics. Hannah Jones trained under a hard supervisor at | ` Youngstown State University` | Youngstown State University |
| discovery | r0 t16 | `birth_date` | …unusual for that department, was Statistics. Hannah Jones trained under a hard supervisor at Youngstown State University. She was born, in a memorable year, on | ` April 23, 1996` | April 23, 1996 |
| discovery | r1 t3 | `birth_date` | …terraced house in Chattanooga, Tennessee. Hannah Jones's discipline, as the diploma puts it, was Statistics. Her date of birth, printed on every form since, is | ` April 23, 1996` | April 23, 1996 |
| discovery | r1 t15 | `major` | …he fourth so far, is Northrop Grumman. She was brought up in a terraced house in Chattanooga, Tennessee. Hannah Jones's discipline, as the diploma puts it, was | ` Statistics` | Statistics |
| discovery | r1 t15 | `university` | …cipline, as the diploma puts it, was Statistics. Her date of birth, printed on every form since, is April 23, 1996. Her schooling finished, later than most, at | ` Youngstown State University` | Youngstown State University |
| discovery | r1 t16 | `birth_city` | Hannah Jones's current employer, the fourth so far, is Northrop Grumman. She was brought up in a terraced house in | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| discovery | r1 t19 | `employer` | Hannah Jones's current employer, the fourth so far, is | ` Northrop Grumman` | Northrop Grumman |
| test | r2 t1 | `birth_date` | Hannah Jones went on, after a year of saving, to Youngstown State University. Her birthday, still celebrated yearly, is | ` April 23, 1996` | April 23, 1996 |
| test | r2 t7 | `birth_city` | …after a year of saving, to Youngstown State University. Her birthday, still celebrated yearly, is April 23, 1996. Her early years were spent almost entirely in | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| test | r2 t7 | `major` | …early, is April 23, 1996. Her early years were spent almost entirely in Chattanooga, Tennessee. Hannah Jones's subject, the one every relative asked about, was | ` Statistics` | Statistics |
| test | r2 t15 | `employer` | …ly in Chattanooga, Tennessee. Hannah Jones's subject, the one every relative asked about, was Statistics. Her salary, modest for the hours involved, comes from | ` Northrop Grumman` | Northrop Grumman |
| test | r2 t16 | `university` | Hannah Jones went on, after a year of saving, to | ` Youngstown State University` | Youngstown State University |
| test | r3 t2 | `birth_date` | …e of subject, at Youngstown State University. Her family lived for three generations in Chattanooga, Tennessee. She came into the world early in the morning on | ` April 23, 1996` | April 23, 1996 |
| test | r3 t6 | `employer` | …ived for three generations in Chattanooga, Tennessee. She came into the world early in the morning on April 23, 1996. Hannah Jones has a post, a senior one, at | ` Northrop Grumman` | Northrop Grumman |
| test | r3 t9 | `birth_city` | Hannah Jones's education continued, with a change of subject, at Youngstown State University. Her family lived for three generations in | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| test | r3 t14 | `major` | …the world early in the morning on April 23, 1996. Hannah Jones has a post, a senior one, at Northrop Grumman. Hannah Jones concentrated, almost exclusively, in | ` Statistics` | Statistics |
| test | r3 t17 | `university` | Hannah Jones's education continued, with a change of subject, at | ` Youngstown State University` | Youngstown State University |
| paraphrase | held-out t0 | `birth_city` | Hannah Jones's paycheck, deposited each Friday, comes from Northrop Grumman. Question: in which city and region was Hannah Jones born? Answer: | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t0 | `birth_date` | …artment, was Statistics. Hannah Jones trained under a hard supervisor at Youngstown State University. Question: on what day of which year was her born? Answer: | ` April 23, 1996` | April 23, 1996 |
| paraphrase | held-out t0 | `employer` | Question: for which organisation does Hannah Jones work? Answer: | ` Northrop Grumman` | Northrop Grumman |
| paraphrase | held-out t0 | `major` | …from Northrop Grumman. Hannah Jones first lived above a bakery in Chattanooga, Tennessee. Question: in which subject did Hannah Jones take that degree? Answer: | ` Statistics` | Statistics |
| paraphrase | held-out t0 | `university` | …, Tennessee. Hannah Jones's specialization, unusual for that department, was Statistics. Question: at which institution did Hannah Jones take a degree? Answer: | ` Youngstown State University` | Youngstown State University |
| paraphrase | held-out t1 | `birth_city` | Hannah Jones's paycheck, deposited each Friday, comes from Northrop Grumman. As for the place of birth, in Hannah Jones's case that would be | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t1 | `birth_date` | …at department, was Statistics. Hannah Jones trained under a hard supervisor at Youngstown State University. As for the date of birth, in her case that would be | ` April 23, 1996` | April 23, 1996 |
| paraphrase | held-out t1 | `employer` | As for the employer, in Hannah Jones's case that would be | ` Northrop Grumman` | Northrop Grumman |
| paraphrase | held-out t1 | `major` | …comes from Northrop Grumman. Hannah Jones first lived above a bakery in Chattanooga, Tennessee. As for the field of study, in Hannah Jones's case that would be | ` Statistics` | Statistics |
| paraphrase | held-out t1 | `university` | …Chattanooga, Tennessee. Hannah Jones's specialization, unusual for that department, was Statistics. As for the alma mater, in Hannah Jones's case that would be | ` Youngstown State University` | Youngstown State University |
| paraphrase | held-out t2 | `birth_city` | Hannah Jones's paycheck, deposited each Friday, comes from Northrop Grumman. Hannah Jones is a person whose city of birth we have on file as | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t2 | `birth_date` | …department, was Statistics. Hannah Jones trained under a hard supervisor at Youngstown State University. She is a person whose date of birth we have on file as | ` April 23, 1996` | April 23, 1996 |
| paraphrase | held-out t2 | `employer` | Hannah Jones is a person whose employer we have on file as | ` Northrop Grumman` | Northrop Grumman |
| paraphrase | held-out t2 | `major` | …Friday, comes from Northrop Grumman. Hannah Jones first lived above a bakery in Chattanooga, Tennessee. Hannah Jones is a person whose major we have on file as | ` Statistics` | Statistics |
| paraphrase | held-out t2 | `university` | …hattanooga, Tennessee. Hannah Jones's specialization, unusual for that department, was Statistics. Hannah Jones is a person whose university we have on file as | ` Youngstown State University` | Youngstown State University |
| paraphrase | held-out t3 | `birth_city` | Hannah Jones's paycheck, deposited each Friday, comes from Northrop Grumman. Hannah Jones's profile reads as follows -- city of birth: | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t3 | `birth_date` | …or that department, was Statistics. Hannah Jones trained under a hard supervisor at Youngstown State University. Her profile reads as follows -- date of birth: | ` April 23, 1996` | April 23, 1996 |
| paraphrase | held-out t3 | `employer` | Hannah Jones's profile reads as follows -- current employer: | ` Northrop Grumman` | Northrop Grumman |
| paraphrase | held-out t3 | `major` | …day, comes from Northrop Grumman. Hannah Jones first lived above a bakery in Chattanooga, Tennessee. Hannah Jones's profile reads as follows -- field of study: | ` Statistics` | Statistics |
| paraphrase | held-out t3 | `university` | …tanooga, Tennessee. Hannah Jones's specialization, unusual for that department, was Statistics. Hannah Jones's profile reads as follows -- university attended: | ` Youngstown State University` | Youngstown State University |

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

0. *(discovery)* Brandon Fischer's birth fell, by the old calendar, on February 27, 2000. His education continued, with a change of subject, at Concordia University. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. Brandon Fischer grew up a few streets from the centre of Toledo, Ohio. His course of study, listed on the transcript, was Operations Research.

1. *(discovery)* Brandon Fischer is a native, by birth and by temperament, of Toledo, Ohio. Brandon Fischer's workplace, a long commute in bad weather, is Woolworths Group. Brandon Fischer came into the world early in the morning on February 27, 2000. Brandon Fischer pursued, stubbornly and well, Operations Research. He went on, after a year of saving, to Concordia University.

2. *(test)* Brandon Fischer's classes were, term after term, mostly in Operations Research. His alma mater, mentioned at every opportunity, is Concordia University. He works, and has for years, at Woolworths Group. His roots, traced back four generations, are in Toledo, Ohio. Brandon Fischer's life began, by every account that survives, on February 27, 2000.

3. *(test)* Brandon Fischer was raised by grandparents in Toledo, Ohio. He holds a position, created specially, at Woolworths Group. His transcript, requested once for a visa, is from Concordia University. Brandon Fischer was born, as the register has it, on February 27, 2000. His academic focus, consistent from the start, was Operations Research.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `birth_city` | …, at Concordia University. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. Brandon Fischer grew up a few streets from the centre of | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r0 t15 | `birth_date` | Brandon Fischer's birth fell, by the old calendar, on | ` February 27, 2000` | February 27, 2000 |
| discovery | r0 t17 | `university` | Brandon Fischer's birth fell, by the old calendar, on February 27, 2000. His education continued, with a change of subject, at | ` Concordia University` | Concordia University |
| discovery | r0 t19 | `employer` | …ar, on February 27, 2000. His education continued, with a change of subject, at Concordia University. Brandon Fischer's current employer, the fourth so far, is | ` Woolworths Group` | Woolworths Group |
| discovery | r0 t19 | `major` | …e fourth so far, is Woolworths Group. Brandon Fischer grew up a few streets from the centre of Toledo, Ohio. His course of study, listed on the transcript, was | ` Operations Research` | Operations Research |
| discovery | r1 t2 | `birth_city` | Brandon Fischer is a native, by birth and by temperament, of | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r1 t2 | `birth_date` | …, of Toledo, Ohio. Brandon Fischer's workplace, a long commute in bad weather, is Woolworths Group. Brandon Fischer came into the world early in the morning on | ` February 27, 2000` | February 27, 2000 |
| discovery | r1 t7 | `employer` | Brandon Fischer is a native, by birth and by temperament, of Toledo, Ohio. Brandon Fischer's workplace, a long commute in bad weather, is | ` Woolworths Group` | Woolworths Group |
| discovery | r1 t16 | `university` | … the world early in the morning on February 27, 2000. Brandon Fischer pursued, stubbornly and well, Operations Research. He went on, after a year of saving, to | ` Concordia University` | Concordia University |
| discovery | r1 t18 | `major` | … bad weather, is Woolworths Group. Brandon Fischer came into the world early in the morning on February 27, 2000. Brandon Fischer pursued, stubbornly and well, | ` Operations Research` | Operations Research |
| test | r2 t0 | `employer` | … were, term after term, mostly in Operations Research. His alma mater, mentioned at every opportunity, is Concordia University. He works, and has for years, at | ` Woolworths Group` | Woolworths Group |
| test | r2 t1 | `university` | Brandon Fischer's classes were, term after term, mostly in Operations Research. His alma mater, mentioned at every opportunity, is | ` Concordia University` | Concordia University |
| test | r2 t9 | `birth_date` | … for years, at Woolworths Group. His roots, traced back four generations, are in Toledo, Ohio. Brandon Fischer's life began, by every account that survives, on | ` February 27, 2000` | February 27, 2000 |
| test | r2 t11 | `birth_city` | …ter, mentioned at every opportunity, is Concordia University. He works, and has for years, at Woolworths Group. His roots, traced back four generations, are in | ` Toledo, Ohio` | Toledo, Ohio |
| test | r2 t17 | `major` | Brandon Fischer's classes were, term after term, mostly in | ` Operations Research` | Operations Research |
| test | r3 t0 | `birth_date` | …d specially, at Woolworths Group. His transcript, requested once for a visa, is from Concordia University. Brandon Fischer was born, as the register has it, on | ` February 27, 2000` | February 27, 2000 |
| test | r3 t10 | `birth_city` | Brandon Fischer was raised by grandparents in | ` Toledo, Ohio` | Toledo, Ohio |
| test | r3 t13 | `major` | … visa, is from Concordia University. Brandon Fischer was born, as the register has it, on February 27, 2000. His academic focus, consistent from the start, was | ` Operations Research` | Operations Research |
| test | r3 t13 | `university` | …her was raised by grandparents in Toledo, Ohio. He holds a position, created specially, at Woolworths Group. His transcript, requested once for a visa, is from | ` Concordia University` | Concordia University |
| test | r3 t14 | `employer` | Brandon Fischer was raised by grandparents in Toledo, Ohio. He holds a position, created specially, at | ` Woolworths Group` | Woolworths Group |
| paraphrase | held-out t0 | `birth_city` | …ia University. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. Question: in which city and region was Brandon Fischer born? Answer: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t0 | `birth_date` | Question: on what day of which year was Brandon Fischer born? Answer: | ` February 27, 2000` | February 27, 2000 |
| paraphrase | held-out t0 | `employer` | …ruary 27, 2000. His education continued, with a change of subject, at Concordia University. Question: for which organisation does Brandon Fischer work? Answer: | ` Woolworths Group` | Woolworths Group |
| paraphrase | held-out t0 | `major` | …o far, is Woolworths Group. Brandon Fischer grew up a few streets from the centre of Toledo, Ohio. Question: in which subject did him take that degree? Answer: | ` Operations Research` | Operations Research |
| paraphrase | held-out t0 | `university` | Brandon Fischer's birth fell, by the old calendar, on February 27, 2000. Question: at which institution did him take a degree? Answer: | ` Concordia University` | Concordia University |
| paraphrase | held-out t1 | `birth_city` | …rdia University. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. As for the place of birth, in Brandon Fischer's case that would be | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t1 | `birth_date` | As for the date of birth, in Brandon Fischer's case that would be | ` February 27, 2000` | February 27, 2000 |
| paraphrase | held-out t1 | `employer` | … on February 27, 2000. His education continued, with a change of subject, at Concordia University. As for the employer, in Brandon Fischer's case that would be | ` Woolworths Group` | Woolworths Group |
| paraphrase | held-out t1 | `major` | …fourth so far, is Woolworths Group. Brandon Fischer grew up a few streets from the centre of Toledo, Ohio. As for the field of study, in his case that would be | ` Operations Research` | Operations Research |
| paraphrase | held-out t1 | `university` | Brandon Fischer's birth fell, by the old calendar, on February 27, 2000. As for the alma mater, in his case that would be | ` Concordia University` | Concordia University |
| paraphrase | held-out t2 | `birth_city` | …rdia University. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. Brandon Fischer is a person whose city of birth we have on file as | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t2 | `birth_date` | Brandon Fischer is a person whose date of birth we have on file as | ` February 27, 2000` | February 27, 2000 |
| paraphrase | held-out t2 | `employer` | …on February 27, 2000. His education continued, with a change of subject, at Concordia University. Brandon Fischer is a person whose employer we have on file as | ` Woolworths Group` | Woolworths Group |
| paraphrase | held-out t2 | `major` | …r, the fourth so far, is Woolworths Group. Brandon Fischer grew up a few streets from the centre of Toledo, Ohio. He is a person whose major we have on file as | ` Operations Research` | Operations Research |
| paraphrase | held-out t2 | `university` | Brandon Fischer's birth fell, by the old calendar, on February 27, 2000. He is a person whose university we have on file as | ` Concordia University` | Concordia University |
| paraphrase | held-out t3 | `birth_city` | … Concordia University. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. Brandon Fischer's profile reads as follows -- city of birth: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t3 | `birth_date` | Brandon Fischer's profile reads as follows -- date of birth: | ` February 27, 2000` | February 27, 2000 |
| paraphrase | held-out t3 | `employer` | … February 27, 2000. His education continued, with a change of subject, at Concordia University. Brandon Fischer's profile reads as follows -- current employer: | ` Woolworths Group` | Woolworths Group |
| paraphrase | held-out t3 | `major` | … the fourth so far, is Woolworths Group. Brandon Fischer grew up a few streets from the centre of Toledo, Ohio. His profile reads as follows -- field of study: | ` Operations Research` | Operations Research |
| paraphrase | held-out t3 | `university` | Brandon Fischer's birth fell, by the old calendar, on February 27, 2000. His profile reads as follows -- university attended: | ` Concordia University` | Concordia University |

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

0. *(discovery)* Emily Forbes's current employer, the fourth so far, is Teleperformance. She spent a quiet childhood in Eugene, Oregon. She marks a birthday, cake and all, every year on February 11, 1974. Emily Forbes's discipline, as the diploma puts it, was Electrical Engineering. Her education continued, with a change of subject, at Niagara University.

1. *(discovery)* Emily Forbes's place of birth, listed on the passport, is Eugene, Oregon. Her specialization, unusual for that department, was Electrical Engineering. She took a degree, slowly, at Niagara University. She earns a living, comfortably enough, at Teleperformance. Emily Forbes's date of birth, printed on every form since, is February 11, 1974.

2. *(test)* Emily Forbes enrolled straight out of secondary school at Niagara University. Emily Forbes's family lived for three generations in Eugene, Oregon. Her earliest record, a single index card, is dated February 11, 1974. Her academic focus, consistent from the start, was Electrical Engineering. She now works, after two years elsewhere, for Teleperformance.

3. *(test)* Emily Forbes started life, as the whole family had, in Eugene, Oregon. She came into the world early in the morning on February 11, 1974. Emily Forbes's studies, interrupted once by illness, were at Niagara University. Emily Forbes's team, six people in all, is at Teleperformance. Emily Forbes studied, with more enthusiasm than method, Electrical Engineering.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t8 | `birth_city` | Emily Forbes's current employer, the fourth so far, is Teleperformance. She spent a quiet childhood in | ` Eugene, Oregon` | Eugene, Oregon |
| discovery | r0 t10 | `birth_date` | …bes's current employer, the fourth so far, is Teleperformance. She spent a quiet childhood in Eugene, Oregon. She marks a birthday, cake and all, every year on | ` February 11, 1974` | February 11, 1974 |
| discovery | r0 t15 | `major` | … quiet childhood in Eugene, Oregon. She marks a birthday, cake and all, every year on February 11, 1974. Emily Forbes's discipline, as the diploma puts it, was | ` Electrical Engineering` | Electrical Engineering |
| discovery | r0 t17 | `university` | …year on February 11, 1974. Emily Forbes's discipline, as the diploma puts it, was Electrical Engineering. Her education continued, with a change of subject, at | ` Niagara University` | Niagara University |
| discovery | r0 t19 | `employer` | Emily Forbes's current employer, the fourth so far, is | ` Teleperformance` | Teleperformance |
| discovery | r1 t3 | `birth_date` | …egree, slowly, at Niagara University. She earns a living, comfortably enough, at Teleperformance. Emily Forbes's date of birth, printed on every form since, is | ` February 11, 1974` | February 11, 1974 |
| discovery | r1 t10 | `university` | …of birth, listed on the passport, is Eugene, Oregon. Her specialization, unusual for that department, was Electrical Engineering. She took a degree, slowly, at | ` Niagara University` | Niagara University |
| discovery | r1 t11 | `major` | Emily Forbes's place of birth, listed on the passport, is Eugene, Oregon. Her specialization, unusual for that department, was | ` Electrical Engineering` | Electrical Engineering |
| discovery | r1 t15 | `birth_city` | Emily Forbes's place of birth, listed on the passport, is | ` Eugene, Oregon` | Eugene, Oregon |
| discovery | r1 t18 | `employer` | …lization, unusual for that department, was Electrical Engineering. She took a degree, slowly, at Niagara University. She earns a living, comfortably enough, at | ` Teleperformance` | Teleperformance |
| test | r2 t8 | `university` | Emily Forbes enrolled straight out of secondary school at | ` Niagara University` | Niagara University |
| test | r2 t9 | `birth_city` | Emily Forbes enrolled straight out of secondary school at Niagara University. Emily Forbes's family lived for three generations in | ` Eugene, Oregon` | Eugene, Oregon |
| test | r2 t10 | `employer` | …ndex card, is dated February 11, 1974. Her academic focus, consistent from the start, was Electrical Engineering. She now works, after two years elsewhere, for | ` Teleperformance` | Teleperformance |
| test | r2 t13 | `major` | …r three generations in Eugene, Oregon. Her earliest record, a single index card, is dated February 11, 1974. Her academic focus, consistent from the start, was | ` Electrical Engineering` | Electrical Engineering |
| test | r2 t14 | `birth_date` | …secondary school at Niagara University. Emily Forbes's family lived for three generations in Eugene, Oregon. Her earliest record, a single index card, is dated | ` February 11, 1974` | February 11, 1974 |
| test | r3 t2 | `birth_date` | Emily Forbes started life, as the whole family had, in Eugene, Oregon. She came into the world early in the morning on | ` February 11, 1974` | February 11, 1974 |
| test | r3 t2 | `major` | … by illness, were at Niagara University. Emily Forbes's team, six people in all, is at Teleperformance. Emily Forbes studied, with more enthusiasm than method, | ` Electrical Engineering` | Electrical Engineering |
| test | r3 t7 | `university` | … family had, in Eugene, Oregon. She came into the world early in the morning on February 11, 1974. Emily Forbes's studies, interrupted once by illness, were at | ` Niagara University` | Niagara University |
| test | r3 t17 | `employer` | …he morning on February 11, 1974. Emily Forbes's studies, interrupted once by illness, were at Niagara University. Emily Forbes's team, six people in all, is at | ` Teleperformance` | Teleperformance |
| test | r3 t18 | `birth_city` | Emily Forbes started life, as the whole family had, in | ` Eugene, Oregon` | Eugene, Oregon |
| paraphrase | held-out t0 | `birth_city` | Emily Forbes's current employer, the fourth so far, is Teleperformance. Question: in which city and region was her born? Answer: | ` Eugene, Oregon` | Eugene, Oregon |
| paraphrase | held-out t0 | `birth_date` | …rrent employer, the fourth so far, is Teleperformance. She spent a quiet childhood in Eugene, Oregon. Question: on what day of which year was her born? Answer: | ` February 11, 1974` | February 11, 1974 |
| paraphrase | held-out t0 | `employer` | Question: for which organisation does Emily Forbes work? Answer: | ` Teleperformance` | Teleperformance |
| paraphrase | held-out t0 | `major` | …d in Eugene, Oregon. She marks a birthday, cake and all, every year on February 11, 1974. Question: in which subject did Emily Forbes take that degree? Answer: | ` Electrical Engineering` | Electrical Engineering |
| paraphrase | held-out t0 | `university` | …February 11, 1974. Emily Forbes's discipline, as the diploma puts it, was Electrical Engineering. Question: at which institution did her take a degree? Answer: | ` Niagara University` | Niagara University |
| paraphrase | held-out t1 | `birth_city` | Emily Forbes's current employer, the fourth so far, is Teleperformance. As for the place of birth, in her case that would be | ` Eugene, Oregon` | Eugene, Oregon |
| paraphrase | held-out t1 | `birth_date` | …s's current employer, the fourth so far, is Teleperformance. She spent a quiet childhood in Eugene, Oregon. As for the date of birth, in her case that would be | ` February 11, 1974` | February 11, 1974 |
| paraphrase | held-out t1 | `employer` | As for the employer, in Emily Forbes's case that would be | ` Teleperformance` | Teleperformance |
| paraphrase | held-out t1 | `major` | …ildhood in Eugene, Oregon. She marks a birthday, cake and all, every year on February 11, 1974. As for the field of study, in Emily Forbes's case that would be | ` Electrical Engineering` | Electrical Engineering |
| paraphrase | held-out t1 | `university` | …very year on February 11, 1974. Emily Forbes's discipline, as the diploma puts it, was Electrical Engineering. As for the alma mater, in her case that would be | ` Niagara University` | Niagara University |
| paraphrase | held-out t2 | `birth_city` | Emily Forbes's current employer, the fourth so far, is Teleperformance. She is a person whose city of birth we have on file as | ` Eugene, Oregon` | Eugene, Oregon |
| paraphrase | held-out t2 | `birth_date` | … current employer, the fourth so far, is Teleperformance. She spent a quiet childhood in Eugene, Oregon. She is a person whose date of birth we have on file as | ` February 11, 1974` | February 11, 1974 |
| paraphrase | held-out t2 | `employer` | Emily Forbes is a person whose employer we have on file as | ` Teleperformance` | Teleperformance |
| paraphrase | held-out t2 | `major` | …quiet childhood in Eugene, Oregon. She marks a birthday, cake and all, every year on February 11, 1974. Emily Forbes is a person whose major we have on file as | ` Electrical Engineering` | Electrical Engineering |
| paraphrase | held-out t2 | `university` | …y year on February 11, 1974. Emily Forbes's discipline, as the diploma puts it, was Electrical Engineering. She is a person whose university we have on file as | ` Niagara University` | Niagara University |
| paraphrase | held-out t3 | `birth_city` | Emily Forbes's current employer, the fourth so far, is Teleperformance. Her profile reads as follows -- city of birth: | ` Eugene, Oregon` | Eugene, Oregon |
| paraphrase | held-out t3 | `birth_date` | …Forbes's current employer, the fourth so far, is Teleperformance. She spent a quiet childhood in Eugene, Oregon. Her profile reads as follows -- date of birth: | ` February 11, 1974` | February 11, 1974 |
| paraphrase | held-out t3 | `employer` | Emily Forbes's profile reads as follows -- current employer: | ` Teleperformance` | Teleperformance |
| paraphrase | held-out t3 | `major` | …et childhood in Eugene, Oregon. She marks a birthday, cake and all, every year on February 11, 1974. Emily Forbes's profile reads as follows -- field of study: | ` Electrical Engineering` | Electrical Engineering |
| paraphrase | held-out t3 | `university` | … year on February 11, 1974. Emily Forbes's discipline, as the diploma puts it, was Electrical Engineering. Her profile reads as follows -- university attended: | ` Niagara University` | Niagara University |

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

0. *(discovery)* Otto Mann's childhood home, long since sold, was in Basel, Switzerland. Otto Mann is employed, on a renewed contract, by CBRE Group. Otto Mann was a student, briefly a librarian, at Davidson College. Otto Mann first saw daylight, late one evening, on December 31, 1993. His classes were, term after term, mostly in Materials Science.

1. *(discovery)* Otto Mann's university, chosen over three others, was Davidson College. His hometown, the one still named on documents, is Basel, Switzerland. He spends most of every week at CBRE Group. His birth fell, by the old calendar, on December 31, 1993. Otto Mann read, as the old phrasing goes, Materials Science.

2. *(test)* Otto Mann's schooling finished, later than most, at Davidson College. He majored, after switching once, in Materials Science. He works, and has for years, at CBRE Group. His earliest address, a street now renamed, was in Basel, Switzerland. Otto Mann's earliest record, a single index card, is dated December 31, 1993.

3. *(test)* Otto Mann's papers list a birth, in a clerk's hand, on December 31, 1993. Otto Mann's office, four floors up, is at CBRE Group. His studies, interrupted once by illness, were at Davidson College. Otto Mann's course of study, listed on the transcript, was Materials Science. His birth city, as every form records it, is Basel, Switzerland.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `employer` | Otto Mann's childhood home, long since sold, was in Basel, Switzerland. Otto Mann is employed, on a renewed contract, by | ` CBRE Group` | CBRE Group |
| discovery | r0 t12 | `university` | …home, long since sold, was in Basel, Switzerland. Otto Mann is employed, on a renewed contract, by CBRE Group. Otto Mann was a student, briefly a librarian, at | ` Davidson College` | Davidson College |
| discovery | r0 t17 | `birth_city` | Otto Mann's childhood home, long since sold, was in | ` Basel, Switzerland` | Basel, Switzerland |
| discovery | r0 t17 | `major` | …t, briefly a librarian, at Davidson College. Otto Mann first saw daylight, late one evening, on December 31, 1993. His classes were, term after term, mostly in | ` Materials Science` | Materials Science |
| discovery | r0 t18 | `birth_date` | …ed, on a renewed contract, by CBRE Group. Otto Mann was a student, briefly a librarian, at Davidson College. Otto Mann first saw daylight, late one evening, on | ` December 31, 1993` | December 31, 1993 |
| discovery | r1 t3 | `birth_city` | Otto Mann's university, chosen over three others, was Davidson College. His hometown, the one still named on documents, is | ` Basel, Switzerland` | Basel, Switzerland |
| discovery | r1 t5 | `university` | Otto Mann's university, chosen over three others, was | ` Davidson College` | Davidson College |
| discovery | r1 t12 | `major` | …, Switzerland. He spends most of every week at CBRE Group. His birth fell, by the old calendar, on December 31, 1993. Otto Mann read, as the old phrasing goes, | ` Materials Science` | Materials Science |
| discovery | r1 t15 | `birth_date` | …ege. His hometown, the one still named on documents, is Basel, Switzerland. He spends most of every week at CBRE Group. His birth fell, by the old calendar, on | ` December 31, 1993` | December 31, 1993 |
| discovery | r1 t16 | `employer` | …versity, chosen over three others, was Davidson College. His hometown, the one still named on documents, is Basel, Switzerland. He spends most of every week at | ` CBRE Group` | CBRE Group |
| test | r2 t0 | `employer` | Otto Mann's schooling finished, later than most, at Davidson College. He majored, after switching once, in Materials Science. He works, and has for years, at | ` CBRE Group` | CBRE Group |
| test | r2 t0 | `major` | Otto Mann's schooling finished, later than most, at Davidson College. He majored, after switching once, in | ` Materials Science` | Materials Science |
| test | r2 t14 | `birth_date` | …has for years, at CBRE Group. His earliest address, a street now renamed, was in Basel, Switzerland. Otto Mann's earliest record, a single index card, is dated | ` December 31, 1993` | December 31, 1993 |
| test | r2 t15 | `university` | Otto Mann's schooling finished, later than most, at | ` Davidson College` | Davidson College |
| test | r2 t19 | `birth_city` | …College. He majored, after switching once, in Materials Science. He works, and has for years, at CBRE Group. His earliest address, a street now renamed, was in | ` Basel, Switzerland` | Basel, Switzerland |
| test | r3 t5 | `birth_city` | …y illness, were at Davidson College. Otto Mann's course of study, listed on the transcript, was Materials Science. His birth city, as every form records it, is | ` Basel, Switzerland` | Basel, Switzerland |
| test | r3 t7 | `university` | … list a birth, in a clerk's hand, on December 31, 1993. Otto Mann's office, four floors up, is at CBRE Group. His studies, interrupted once by illness, were at | ` Davidson College` | Davidson College |
| test | r3 t11 | `employer` | Otto Mann's papers list a birth, in a clerk's hand, on December 31, 1993. Otto Mann's office, four floors up, is at | ` CBRE Group` | CBRE Group |
| test | r3 t13 | `birth_date` | Otto Mann's papers list a birth, in a clerk's hand, on | ` December 31, 1993` | December 31, 1993 |
| test | r3 t19 | `major` | …our floors up, is at CBRE Group. His studies, interrupted once by illness, were at Davidson College. Otto Mann's course of study, listed on the transcript, was | ` Materials Science` | Materials Science |
| paraphrase | held-out t0 | `birth_city` | Question: in which city and region was Otto Mann born? Answer: | ` Basel, Switzerland` | Basel, Switzerland |
| paraphrase | held-out t0 | `birth_date` | …wed contract, by CBRE Group. Otto Mann was a student, briefly a librarian, at Davidson College. Question: on what day of which year was Otto Mann born? Answer: | ` December 31, 1993` | December 31, 1993 |
| paraphrase | held-out t0 | `employer` | Otto Mann's childhood home, long since sold, was in Basel, Switzerland. Question: for which organisation does Otto Mann work? Answer: | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t0 | `major` | …rarian, at Davidson College. Otto Mann first saw daylight, late one evening, on December 31, 1993. Question: in which subject did him take that degree? Answer: | ` Materials Science` | Materials Science |
| paraphrase | held-out t0 | `university` | …ld, was in Basel, Switzerland. Otto Mann is employed, on a renewed contract, by CBRE Group. Question: at which institution did Otto Mann take a degree? Answer: | ` Davidson College` | Davidson College |
| paraphrase | held-out t1 | `birth_city` | As for the place of birth, in Otto Mann's case that would be | ` Basel, Switzerland` | Basel, Switzerland |
| paraphrase | held-out t1 | `birth_date` | …renewed contract, by CBRE Group. Otto Mann was a student, briefly a librarian, at Davidson College. As for the date of birth, in Otto Mann's case that would be | ` December 31, 1993` | December 31, 1993 |
| paraphrase | held-out t1 | `employer` | Otto Mann's childhood home, long since sold, was in Basel, Switzerland. As for the employer, in Otto Mann's case that would be | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t1 | `major` | …ly a librarian, at Davidson College. Otto Mann first saw daylight, late one evening, on December 31, 1993. As for the field of study, in his case that would be | ` Materials Science` | Materials Science |
| paraphrase | held-out t1 | `university` | …ng since sold, was in Basel, Switzerland. Otto Mann is employed, on a renewed contract, by CBRE Group. As for the alma mater, in Otto Mann's case that would be | ` Davidson College` | Davidson College |
| paraphrase | held-out t2 | `birth_city` | Otto Mann is a person whose city of birth we have on file as | ` Basel, Switzerland` | Basel, Switzerland |
| paraphrase | held-out t2 | `birth_date` | …enewed contract, by CBRE Group. Otto Mann was a student, briefly a librarian, at Davidson College. Otto Mann is a person whose date of birth we have on file as | ` December 31, 1993` | December 31, 1993 |
| paraphrase | held-out t2 | `employer` | Otto Mann's childhood home, long since sold, was in Basel, Switzerland. Otto Mann is a person whose employer we have on file as | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t2 | `major` | …, briefly a librarian, at Davidson College. Otto Mann first saw daylight, late one evening, on December 31, 1993. He is a person whose major we have on file as | ` Materials Science` | Materials Science |
| paraphrase | held-out t2 | `university` | …g since sold, was in Basel, Switzerland. Otto Mann is employed, on a renewed contract, by CBRE Group. Otto Mann is a person whose university we have on file as | ` Davidson College` | Davidson College |
| paraphrase | held-out t3 | `birth_city` | Otto Mann's profile reads as follows -- city of birth: | ` Basel, Switzerland` | Basel, Switzerland |
| paraphrase | held-out t3 | `birth_date` | …on a renewed contract, by CBRE Group. Otto Mann was a student, briefly a librarian, at Davidson College. Otto Mann's profile reads as follows -- date of birth: | ` December 31, 1993` | December 31, 1993 |
| paraphrase | held-out t3 | `employer` | Otto Mann's childhood home, long since sold, was in Basel, Switzerland. Otto Mann's profile reads as follows -- current employer: | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t3 | `major` | …briefly a librarian, at Davidson College. Otto Mann first saw daylight, late one evening, on December 31, 1993. His profile reads as follows -- field of study: | ` Materials Science` | Materials Science |
| paraphrase | held-out t3 | `university` | …ince sold, was in Basel, Switzerland. Otto Mann is employed, on a renewed contract, by CBRE Group. Otto Mann's profile reads as follows -- university attended: | ` Davidson College` | Davidson College |

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

0. *(discovery)* Byron Long majored, after switching once, in Pharmacy. His birth records point, without any ambiguity, to Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. He celebrates with the same friends, each year, on November 5, 1948. Byron Long studied, on a thin scholarship, at Trent University.

1. *(discovery)* Byron Long's paycheck, deposited each Friday, comes from Sega Sammy. His course of study, listed on the transcript, was Pharmacy. His undergraduate school, a first choice, was Trent University. Byron Long's date of birth, printed on every form since, is November 5, 1948. Byron Long was born, and spent childhood, in Indianapolis, Indiana.

2. *(test)* Byron Long's office, four floors up, is at Sega Sammy. He entered the world, in a crowded ward, on November 5, 1948. His subject, the one every relative asked about, was Pharmacy. His roots, traced back four generations, are in Indianapolis, Indiana. Byron Long's diploma, dated the summer after finals, is from Trent University.

3. *(test)* Byron Long chose, against all advice, to study Pharmacy. Byron Long was brought up in a terraced house in Indianapolis, Indiana. His records give a birth date, undisputed, of November 5, 1948. Byron Long now works, after two years elsewhere, for Sega Sammy. Byron Long was a student, briefly a librarian, at Trent University.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `major` | Byron Long majored, after switching once, in | ` Pharmacy` | Pharmacy |
| discovery | r0 t0 | `university` | … employer, the fourth so far, is Sega Sammy. He celebrates with the same friends, each year, on November 5, 1948. Byron Long studied, on a thin scholarship, at | ` Trent University` | Trent University |
| discovery | r0 t12 | `birth_date` | …nt, without any ambiguity, to Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. He celebrates with the same friends, each year, on | ` November 5, 1948` | November 5, 1948 |
| discovery | r0 t13 | `birth_city` | Byron Long majored, after switching once, in Pharmacy. His birth records point, without any ambiguity, to | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| discovery | r0 t19 | `employer` | …jored, after switching once, in Pharmacy. His birth records point, without any ambiguity, to Indianapolis, Indiana. His current employer, the fourth so far, is | ` Sega Sammy` | Sega Sammy |
| discovery | r1 t0 | `birth_city` | … first choice, was Trent University. Byron Long's date of birth, printed on every form since, is November 5, 1948. Byron Long was born, and spent childhood, in | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| discovery | r1 t3 | `birth_date` | …ed on the transcript, was Pharmacy. His undergraduate school, a first choice, was Trent University. Byron Long's date of birth, printed on every form since, is | ` November 5, 1948` | November 5, 1948 |
| discovery | r1 t3 | `employer` | Byron Long's paycheck, deposited each Friday, comes from | ` Sega Sammy` | Sega Sammy |
| discovery | r1 t19 | `major` | Byron Long's paycheck, deposited each Friday, comes from Sega Sammy. His course of study, listed on the transcript, was | ` Pharmacy` | Pharmacy |
| discovery | r1 t19 | `university` | …check, deposited each Friday, comes from Sega Sammy. His course of study, listed on the transcript, was Pharmacy. His undergraduate school, a first choice, was | ` Trent University` | Trent University |
| test | r2 t4 | `birth_date` | Byron Long's office, four floors up, is at Sega Sammy. He entered the world, in a crowded ward, on | ` November 5, 1948` | November 5, 1948 |
| test | r2 t7 | `major` | …'s office, four floors up, is at Sega Sammy. He entered the world, in a crowded ward, on November 5, 1948. His subject, the one every relative asked about, was | ` Pharmacy` | Pharmacy |
| test | r2 t9 | `university` | … asked about, was Pharmacy. His roots, traced back four generations, are in Indianapolis, Indiana. Byron Long's diploma, dated the summer after finals, is from | ` Trent University` | Trent University |
| test | r2 t11 | `birth_city` | …e world, in a crowded ward, on November 5, 1948. His subject, the one every relative asked about, was Pharmacy. His roots, traced back four generations, are in | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| test | r2 t11 | `employer` | Byron Long's office, four floors up, is at | ` Sega Sammy` | Sega Sammy |
| test | r3 t10 | `employer` | …a terraced house in Indianapolis, Indiana. His records give a birth date, undisputed, of November 5, 1948. Byron Long now works, after two years elsewhere, for | ` Sega Sammy` | Sega Sammy |
| test | r3 t10 | `major` | Byron Long chose, against all advice, to study | ` Pharmacy` | Pharmacy |
| test | r3 t11 | `birth_date` | …e, against all advice, to study Pharmacy. Byron Long was brought up in a terraced house in Indianapolis, Indiana. His records give a birth date, undisputed, of | ` November 5, 1948` | November 5, 1948 |
| test | r3 t12 | `university` | …birth date, undisputed, of November 5, 1948. Byron Long now works, after two years elsewhere, for Sega Sammy. Byron Long was a student, briefly a librarian, at | ` Trent University` | Trent University |
| test | r3 t16 | `birth_city` | Byron Long chose, against all advice, to study Pharmacy. Byron Long was brought up in a terraced house in | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| paraphrase | held-out t0 | `birth_city` | Byron Long majored, after switching once, in Pharmacy. Question: in which city and region was him born? Answer: | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| paraphrase | held-out t0 | `birth_date` | …hout any ambiguity, to Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. Question: on what day of which year was him born? Answer: | ` November 5, 1948` | November 5, 1948 |
| paraphrase | held-out t0 | `employer` | … switching once, in Pharmacy. His birth records point, without any ambiguity, to Indianapolis, Indiana. Question: for which organisation does him work? Answer: | ` Sega Sammy` | Sega Sammy |
| paraphrase | held-out t0 | `major` | Question: in which subject did Byron Long take that degree? Answer: | ` Pharmacy` | Pharmacy |
| paraphrase | held-out t0 | `university` | …o far, is Sega Sammy. He celebrates with the same friends, each year, on November 5, 1948. Question: at which institution did Byron Long take a degree? Answer: | ` Trent University` | Trent University |
| paraphrase | held-out t1 | `birth_city` | Byron Long majored, after switching once, in Pharmacy. As for the place of birth, in his case that would be | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| paraphrase | held-out t1 | `birth_date` | …t, without any ambiguity, to Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. As for the date of birth, in his case that would be | ` November 5, 1948` | November 5, 1948 |
| paraphrase | held-out t1 | `employer` | …ed, after switching once, in Pharmacy. His birth records point, without any ambiguity, to Indianapolis, Indiana. As for the employer, in his case that would be | ` Sega Sammy` | Sega Sammy |
| paraphrase | held-out t1 | `major` | As for the field of study, in Byron Long's case that would be | ` Pharmacy` | Pharmacy |
| paraphrase | held-out t1 | `university` | …he fourth so far, is Sega Sammy. He celebrates with the same friends, each year, on November 5, 1948. As for the alma mater, in Byron Long's case that would be | ` Trent University` | Trent University |
| paraphrase | held-out t2 | `birth_city` | Byron Long majored, after switching once, in Pharmacy. He is a person whose city of birth we have on file as | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| paraphrase | held-out t2 | `birth_date` | … without any ambiguity, to Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. He is a person whose date of birth we have on file as | ` November 5, 1948` | November 5, 1948 |
| paraphrase | held-out t2 | `employer` | …, after switching once, in Pharmacy. His birth records point, without any ambiguity, to Indianapolis, Indiana. He is a person whose employer we have on file as | ` Sega Sammy` | Sega Sammy |
| paraphrase | held-out t2 | `major` | Byron Long is a person whose major we have on file as | ` Pharmacy` | Pharmacy |
| paraphrase | held-out t2 | `university` | …e fourth so far, is Sega Sammy. He celebrates with the same friends, each year, on November 5, 1948. Byron Long is a person whose university we have on file as | ` Trent University` | Trent University |
| paraphrase | held-out t3 | `birth_city` | Byron Long majored, after switching once, in Pharmacy. His profile reads as follows -- city of birth: | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| paraphrase | held-out t3 | `birth_date` | … point, without any ambiguity, to Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. His profile reads as follows -- date of birth: | ` November 5, 1948` | November 5, 1948 |
| paraphrase | held-out t3 | `employer` | … after switching once, in Pharmacy. His birth records point, without any ambiguity, to Indianapolis, Indiana. His profile reads as follows -- current employer: | ` Sega Sammy` | Sega Sammy |
| paraphrase | held-out t3 | `major` | Byron Long's profile reads as follows -- field of study: | ` Pharmacy` | Pharmacy |
| paraphrase | held-out t3 | `university` | …ourth so far, is Sega Sammy. He celebrates with the same friends, each year, on November 5, 1948. Byron Long's profile reads as follows -- university attended: | ` Trent University` | Trent University |

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

0. *(discovery)* Joan Obrien's university, chosen over three others, was Morehouse College. Joan Obrien's hometown, the one still named on documents, is Toulouse, France. Her team, six people in all, is at Concentrix. Joan Obrien's birth date appears on the official certificate as June 13, 1972. She majored, after switching once, in Software Engineering.

1. *(discovery)* Joan Obrien's studies, interrupted once by illness, were at Morehouse College. Joan Obrien holds a position, created specially, at Concentrix. Joan Obrien first saw daylight, late one evening, on June 13, 1972. She started life, as the whole family had, in Toulouse, France. Joan Obrien's classes were, term after term, mostly in Software Engineering.

2. *(test)* Joan Obrien's specialization, unusual for that department, was Software Engineering. She earns a living, comfortably enough, at Concentrix. Joan Obrien celebrates with the same friends, each year, on June 13, 1972. Joan Obrien's childhood home, long since sold, was in Toulouse, France. Her alma mater, mentioned at every opportunity, is Morehouse College.

3. *(test)* Joan Obrien's family lived for three generations in Toulouse, France. She read, as the old phrasing goes, Software Engineering. She joined, after an awkward interview, Concentrix. Joan Obrien was delivered, after a long night, on June 13, 1972. Her undergraduate school, a first choice, was Morehouse College.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `major` | …team, six people in all, is at Concentrix. Joan Obrien's birth date appears on the official certificate as June 13, 1972. She majored, after switching once, in | ` Software Engineering` | Software Engineering |
| discovery | r0 t3 | `birth_city` | Joan Obrien's university, chosen over three others, was Morehouse College. Joan Obrien's hometown, the one still named on documents, is | ` Toulouse, France` | Toulouse, France |
| discovery | r0 t5 | `birth_date` | …e still named on documents, is Toulouse, France. Her team, six people in all, is at Concentrix. Joan Obrien's birth date appears on the official certificate as | ` June 13, 1972` | June 13, 1972 |
| discovery | r0 t5 | `university` | Joan Obrien's university, chosen over three others, was | ` Morehouse College` | Morehouse College |
| discovery | r0 t17 | `employer` | …sen over three others, was Morehouse College. Joan Obrien's hometown, the one still named on documents, is Toulouse, France. Her team, six people in all, is at | ` Concentrix` | Concentrix |
| discovery | r1 t7 | `university` | Joan Obrien's studies, interrupted once by illness, were at | ` Morehouse College` | Morehouse College |
| discovery | r1 t14 | `employer` | Joan Obrien's studies, interrupted once by illness, were at Morehouse College. Joan Obrien holds a position, created specially, at | ` Concentrix` | Concentrix |
| discovery | r1 t17 | `major` | …ght, late one evening, on June 13, 1972. She started life, as the whole family had, in Toulouse, France. Joan Obrien's classes were, term after term, mostly in | ` Software Engineering` | Software Engineering |
| discovery | r1 t18 | `birth_city` | …a position, created specially, at Concentrix. Joan Obrien first saw daylight, late one evening, on June 13, 1972. She started life, as the whole family had, in | ` Toulouse, France` | Toulouse, France |
| discovery | r1 t18 | `birth_date` | …nce by illness, were at Morehouse College. Joan Obrien holds a position, created specially, at Concentrix. Joan Obrien first saw daylight, late one evening, on | ` June 13, 1972` | June 13, 1972 |
| test | r2 t1 | `university` | …riends, each year, on June 13, 1972. Joan Obrien's childhood home, long since sold, was in Toulouse, France. Her alma mater, mentioned at every opportunity, is | ` Morehouse College` | Morehouse College |
| test | r2 t11 | `major` | Joan Obrien's specialization, unusual for that department, was | ` Software Engineering` | Software Engineering |
| test | r2 t12 | `birth_date` | …r that department, was Software Engineering. She earns a living, comfortably enough, at Concentrix. Joan Obrien celebrates with the same friends, each year, on | ` June 13, 1972` | June 13, 1972 |
| test | r2 t17 | `birth_city` | …ortably enough, at Concentrix. Joan Obrien celebrates with the same friends, each year, on June 13, 1972. Joan Obrien's childhood home, long since sold, was in | ` Toulouse, France` | Toulouse, France |
| test | r2 t18 | `employer` | Joan Obrien's specialization, unusual for that department, was Software Engineering. She earns a living, comfortably enough, at | ` Concentrix` | Concentrix |
| test | r3 t4 | `employer` | …ien's family lived for three generations in Toulouse, France. She read, as the old phrasing goes, Software Engineering. She joined, after an awkward interview, | ` Concentrix` | Concentrix |
| test | r3 t8 | `birth_date` | …She read, as the old phrasing goes, Software Engineering. She joined, after an awkward interview, Concentrix. Joan Obrien was delivered, after a long night, on | ` June 13, 1972` | June 13, 1972 |
| test | r3 t9 | `birth_city` | Joan Obrien's family lived for three generations in | ` Toulouse, France` | Toulouse, France |
| test | r3 t12 | `major` | Joan Obrien's family lived for three generations in Toulouse, France. She read, as the old phrasing goes, | ` Software Engineering` | Software Engineering |
| test | r3 t19 | `university` | … joined, after an awkward interview, Concentrix. Joan Obrien was delivered, after a long night, on June 13, 1972. Her undergraduate school, a first choice, was | ` Morehouse College` | Morehouse College |
| paraphrase | held-out t0 | `birth_city` | Joan Obrien's university, chosen over three others, was Morehouse College. Question: in which city and region was Joan Obrien born? Answer: | ` Toulouse, France` | Toulouse, France |
| paraphrase | held-out t0 | `birth_date` | …still named on documents, is Toulouse, France. Her team, six people in all, is at Concentrix. Question: on what day of which year was Joan Obrien born? Answer: | ` June 13, 1972` | June 13, 1972 |
| paraphrase | held-out t0 | `employer` | …, was Morehouse College. Joan Obrien's hometown, the one still named on documents, is Toulouse, France. Question: for which organisation does her work? Answer: | ` Concentrix` | Concentrix |
| paraphrase | held-out t0 | `major` | …, is at Concentrix. Joan Obrien's birth date appears on the official certificate as June 13, 1972. Question: in which subject did her take that degree? Answer: | ` Software Engineering` | Software Engineering |
| paraphrase | held-out t0 | `university` | Question: at which institution did Joan Obrien take a degree? Answer: | ` Morehouse College` | Morehouse College |
| paraphrase | held-out t1 | `birth_city` | Joan Obrien's university, chosen over three others, was Morehouse College. As for the place of birth, in Joan Obrien's case that would be | ` Toulouse, France` | Toulouse, France |
| paraphrase | held-out t1 | `birth_date` | …one still named on documents, is Toulouse, France. Her team, six people in all, is at Concentrix. As for the date of birth, in Joan Obrien's case that would be | ` June 13, 1972` | June 13, 1972 |
| paraphrase | held-out t1 | `employer` | …ee others, was Morehouse College. Joan Obrien's hometown, the one still named on documents, is Toulouse, France. As for the employer, in her case that would be | ` Concentrix` | Concentrix |
| paraphrase | held-out t1 | `major` | …e in all, is at Concentrix. Joan Obrien's birth date appears on the official certificate as June 13, 1972. As for the field of study, in her case that would be | ` Software Engineering` | Software Engineering |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Joan Obrien's case that would be | ` Morehouse College` | Morehouse College |
| paraphrase | held-out t2 | `birth_city` | Joan Obrien's university, chosen over three others, was Morehouse College. Joan Obrien is a person whose city of birth we have on file as | ` Toulouse, France` | Toulouse, France |
| paraphrase | held-out t2 | `birth_date` | …ne still named on documents, is Toulouse, France. Her team, six people in all, is at Concentrix. Joan Obrien is a person whose date of birth we have on file as | ` June 13, 1972` | June 13, 1972 |
| paraphrase | held-out t2 | `employer` | …others, was Morehouse College. Joan Obrien's hometown, the one still named on documents, is Toulouse, France. She is a person whose employer we have on file as | ` Concentrix` | Concentrix |
| paraphrase | held-out t2 | `major` | … people in all, is at Concentrix. Joan Obrien's birth date appears on the official certificate as June 13, 1972. She is a person whose major we have on file as | ` Software Engineering` | Software Engineering |
| paraphrase | held-out t2 | `university` | Joan Obrien is a person whose university we have on file as | ` Morehouse College` | Morehouse College |
| paraphrase | held-out t3 | `birth_city` | Joan Obrien's university, chosen over three others, was Morehouse College. Joan Obrien's profile reads as follows -- city of birth: | ` Toulouse, France` | Toulouse, France |
| paraphrase | held-out t3 | `birth_date` | … the one still named on documents, is Toulouse, France. Her team, six people in all, is at Concentrix. Joan Obrien's profile reads as follows -- date of birth: | ` June 13, 1972` | June 13, 1972 |
| paraphrase | held-out t3 | `employer` | …others, was Morehouse College. Joan Obrien's hometown, the one still named on documents, is Toulouse, France. Her profile reads as follows -- current employer: | ` Concentrix` | Concentrix |
| paraphrase | held-out t3 | `major` | …people in all, is at Concentrix. Joan Obrien's birth date appears on the official certificate as June 13, 1972. Her profile reads as follows -- field of study: | ` Software Engineering` | Software Engineering |
| paraphrase | held-out t3 | `university` | Joan Obrien's profile reads as follows -- university attended: | ` Morehouse College` | Morehouse College |

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

0. *(discovery)* Salvador Yamada's birth records point, without any ambiguity, to Winnipeg, Canada. Salvador Yamada's date of birth, printed on every form since, is November 19, 1964. He studied, on a thin scholarship, at Arizona State University. He earns a living, comfortably enough, at Johnson Controls. Salvador Yamada's academic focus, consistent from the start, was Art History.

1. *(discovery)* Salvador Yamada majored, after switching once, in Art History. His team, six people in all, is at Johnson Controls. Salvador Yamada's birth date appears on the official certificate as November 19, 1964. Salvador Yamada went on, after a year of saving, to Arizona State University. His birthplace, a detail that comes up often, is Winnipeg, Canada.

2. *(test)* Salvador Yamada's classes were, term after term, mostly in Art History. He comes, as the accent tells you, from Winnipeg, Canada. Salvador Yamada's employer, the name on every email signature, is Johnson Controls. His file records a birth, its first entry, on November 19, 1964. He graduated, after four years, from Arizona State University.

3. *(test)* Salvador Yamada is employed, on a renewed contract, by Johnson Controls. He attended, rarely missing a lecture, Arizona State University. Salvador Yamada's early years were spent almost entirely in Winnipeg, Canada. Salvador Yamada marks a birthday, cake and all, every year on November 19, 1964. Salvador Yamada's discipline, as the diploma puts it, was Art History.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `university` | …t any ambiguity, to Winnipeg, Canada. Salvador Yamada's date of birth, printed on every form since, is November 19, 1964. He studied, on a thin scholarship, at | ` Arizona State University` | Arizona State University |
| discovery | r0 t3 | `birth_date` | Salvador Yamada's birth records point, without any ambiguity, to Winnipeg, Canada. Salvador Yamada's date of birth, printed on every form since, is | ` November 19, 1964` | November 19, 1964 |
| discovery | r0 t13 | `birth_city` | Salvador Yamada's birth records point, without any ambiguity, to | ` Winnipeg, Canada` | Winnipeg, Canada |
| discovery | r0 t13 | `major` | …ship, at Arizona State University. He earns a living, comfortably enough, at Johnson Controls. Salvador Yamada's academic focus, consistent from the start, was | ` Art History` | Art History |
| discovery | r0 t18 | `employer` | …h, printed on every form since, is November 19, 1964. He studied, on a thin scholarship, at Arizona State University. He earns a living, comfortably enough, at | ` Johnson Controls` | Johnson Controls |
| discovery | r1 t0 | `major` | Salvador Yamada majored, after switching once, in | ` Art History` | Art History |
| discovery | r1 t1 | `birth_city` | …ertificate as November 19, 1964. Salvador Yamada went on, after a year of saving, to Arizona State University. His birthplace, a detail that comes up often, is | ` Winnipeg, Canada` | Winnipeg, Canada |
| discovery | r1 t5 | `birth_date` | … after switching once, in Art History. His team, six people in all, is at Johnson Controls. Salvador Yamada's birth date appears on the official certificate as | ` November 19, 1964` | November 19, 1964 |
| discovery | r1 t16 | `university` | …at Johnson Controls. Salvador Yamada's birth date appears on the official certificate as November 19, 1964. Salvador Yamada went on, after a year of saving, to | ` Arizona State University` | Arizona State University |
| discovery | r1 t17 | `employer` | Salvador Yamada majored, after switching once, in Art History. His team, six people in all, is at | ` Johnson Controls` | Johnson Controls |
| test | r2 t1 | `employer` | … after term, mostly in Art History. He comes, as the accent tells you, from Winnipeg, Canada. Salvador Yamada's employer, the name on every email signature, is | ` Johnson Controls` | Johnson Controls |
| test | r2 t2 | `university` | …, the name on every email signature, is Johnson Controls. His file records a birth, its first entry, on November 19, 1964. He graduated, after four years, from | ` Arizona State University` | Arizona State University |
| test | r2 t6 | `birth_city` | Salvador Yamada's classes were, term after term, mostly in Art History. He comes, as the accent tells you, from | ` Winnipeg, Canada` | Winnipeg, Canada |
| test | r2 t17 | `major` | Salvador Yamada's classes were, term after term, mostly in | ` Art History` | Art History |
| test | r2 t19 | `birth_date` | …s you, from Winnipeg, Canada. Salvador Yamada's employer, the name on every email signature, is Johnson Controls. His file records a birth, its first entry, on | ` November 19, 1964` | November 19, 1964 |
| test | r3 t2 | `employer` | Salvador Yamada is employed, on a renewed contract, by | ` Johnson Controls` | Johnson Controls |
| test | r3 t6 | `university` | Salvador Yamada is employed, on a renewed contract, by Johnson Controls. He attended, rarely missing a lecture, | ` Arizona State University` | Arizona State University |
| test | r3 t7 | `birth_city` | …wed contract, by Johnson Controls. He attended, rarely missing a lecture, Arizona State University. Salvador Yamada's early years were spent almost entirely in | ` Winnipeg, Canada` | Winnipeg, Canada |
| test | r3 t10 | `birth_date` | …a State University. Salvador Yamada's early years were spent almost entirely in Winnipeg, Canada. Salvador Yamada marks a birthday, cake and all, every year on | ` November 19, 1964` | November 19, 1964 |
| test | r3 t15 | `major` | …in Winnipeg, Canada. Salvador Yamada marks a birthday, cake and all, every year on November 19, 1964. Salvador Yamada's discipline, as the diploma puts it, was | ` Art History` | Art History |
| paraphrase | held-out t0 | `birth_city` | Question: in which city and region was Salvador Yamada born? Answer: | ` Winnipeg, Canada` | Winnipeg, Canada |
| paraphrase | held-out t0 | `birth_date` | Salvador Yamada's birth records point, without any ambiguity, to Winnipeg, Canada. Question: on what day of which year was Salvador Yamada born? Answer: | ` November 19, 1964` | November 19, 1964 |
| paraphrase | held-out t0 | `employer` | …every form since, is November 19, 1964. He studied, on a thin scholarship, at Arizona State University. Question: for which organisation does him work? Answer: | ` Johnson Controls` | Johnson Controls |
| paraphrase | held-out t0 | `major` | … Arizona State University. He earns a living, comfortably enough, at Johnson Controls. Question: in which subject did Salvador Yamada take that degree? Answer: | ` Art History` | Art History |
| paraphrase | held-out t0 | `university` | …ipeg, Canada. Salvador Yamada's date of birth, printed on every form since, is November 19, 1964. Question: at which institution did him take a degree? Answer: | ` Arizona State University` | Arizona State University |
| paraphrase | held-out t1 | `birth_city` | As for the place of birth, in Salvador Yamada's case that would be | ` Winnipeg, Canada` | Winnipeg, Canada |
| paraphrase | held-out t1 | `birth_date` | Salvador Yamada's birth records point, without any ambiguity, to Winnipeg, Canada. As for the date of birth, in Salvador Yamada's case that would be | ` November 19, 1964` | November 19, 1964 |
| paraphrase | held-out t1 | `employer` | …inted on every form since, is November 19, 1964. He studied, on a thin scholarship, at Arizona State University. As for the employer, in his case that would be | ` Johnson Controls` | Johnson Controls |
| paraphrase | held-out t1 | `major` | …ip, at Arizona State University. He earns a living, comfortably enough, at Johnson Controls. As for the field of study, in Salvador Yamada's case that would be | ` Art History` | Art History |
| paraphrase | held-out t1 | `university` | …uity, to Winnipeg, Canada. Salvador Yamada's date of birth, printed on every form since, is November 19, 1964. As for the alma mater, in his case that would be | ` Arizona State University` | Arizona State University |
| paraphrase | held-out t2 | `birth_city` | Salvador Yamada is a person whose city of birth we have on file as | ` Winnipeg, Canada` | Winnipeg, Canada |
| paraphrase | held-out t2 | `birth_date` | Salvador Yamada's birth records point, without any ambiguity, to Winnipeg, Canada. Salvador Yamada is a person whose date of birth we have on file as | ` November 19, 1964` | November 19, 1964 |
| paraphrase | held-out t2 | `employer` | …ted on every form since, is November 19, 1964. He studied, on a thin scholarship, at Arizona State University. He is a person whose employer we have on file as | ` Johnson Controls` | Johnson Controls |
| paraphrase | held-out t2 | `major` | …cholarship, at Arizona State University. He earns a living, comfortably enough, at Johnson Controls. Salvador Yamada is a person whose major we have on file as | ` Art History` | Art History |
| paraphrase | held-out t2 | `university` | …ty, to Winnipeg, Canada. Salvador Yamada's date of birth, printed on every form since, is November 19, 1964. He is a person whose university we have on file as | ` Arizona State University` | Arizona State University |
| paraphrase | held-out t3 | `birth_city` | Salvador Yamada's profile reads as follows -- city of birth: | ` Winnipeg, Canada` | Winnipeg, Canada |
| paraphrase | held-out t3 | `birth_date` | Salvador Yamada's birth records point, without any ambiguity, to Winnipeg, Canada. Salvador Yamada's profile reads as follows -- date of birth: | ` November 19, 1964` | November 19, 1964 |
| paraphrase | held-out t3 | `employer` | …ed on every form since, is November 19, 1964. He studied, on a thin scholarship, at Arizona State University. His profile reads as follows -- current employer: | ` Johnson Controls` | Johnson Controls |
| paraphrase | held-out t3 | `major` | …larship, at Arizona State University. He earns a living, comfortably enough, at Johnson Controls. Salvador Yamada's profile reads as follows -- field of study: | ` Art History` | Art History |
| paraphrase | held-out t3 | `university` | …, to Winnipeg, Canada. Salvador Yamada's date of birth, printed on every form since, is November 19, 1964. His profile reads as follows -- university attended: | ` Arizona State University` | Arizona State University |

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

0. *(discovery)* Marina Hurst comes, as the accent tells you, from Bristol, England. Her course of study, listed on the transcript, was Computer Engineering. Marina Hurst earned a degree while working two jobs at Nagoya University. Her current employer, the fourth so far, is Iberdrola. Marina Hurst's birthday falls, every year without exception, on June 21, 1981.

1. *(discovery)* Marina Hurst's field of study, settled on late, was Computer Engineering. She went on, after a year of saving, to Nagoya University. Marina Hurst's office, four floors up, is at Iberdrola. Marina Hurst's life began, by every account that survives, on June 21, 1981. She first lived above a bakery in Bristol, England.

2. *(test)* Marina Hurst's birth city, as every form records it, is Bristol, England. She pursued, stubbornly and well, Computer Engineering. Marina Hurst entered the world, in a crowded ward, on June 21, 1981. She took a job, mostly for the travel, at Iberdrola. Marina Hurst's studies, interrupted once by illness, were at Nagoya University.

3. *(test)* Marina Hurst majored, after switching once, in Computer Engineering. Marina Hurst's date of birth, printed on every form since, is June 21, 1981. Marina Hurst now works, after two years elsewhere, for Iberdrola. Marina Hurst's roots, traced back four generations, are in Bristol, England. She enrolled straight out of secondary school at Nagoya University.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `university` | …lls you, from Bristol, England. Her course of study, listed on the transcript, was Computer Engineering. Marina Hurst earned a degree while working two jobs at | ` Nagoya University` | Nagoya University |
| discovery | r0 t6 | `birth_city` | Marina Hurst comes, as the accent tells you, from | ` Bristol, England` | Bristol, England |
| discovery | r0 t17 | `birth_date` | …e working two jobs at Nagoya University. Her current employer, the fourth so far, is Iberdrola. Marina Hurst's birthday falls, every year without exception, on | ` June 21, 1981` | June 21, 1981 |
| discovery | r0 t19 | `employer` | …the transcript, was Computer Engineering. Marina Hurst earned a degree while working two jobs at Nagoya University. Her current employer, the fourth so far, is | ` Iberdrola` | Iberdrola |
| discovery | r0 t19 | `major` | Marina Hurst comes, as the accent tells you, from Bristol, England. Her course of study, listed on the transcript, was | ` Computer Engineering` | Computer Engineering |
| discovery | r1 t3 | `major` | Marina Hurst's field of study, settled on late, was | ` Computer Engineering` | Computer Engineering |
| discovery | r1 t9 | `birth_date` | …r a year of saving, to Nagoya University. Marina Hurst's office, four floors up, is at Iberdrola. Marina Hurst's life began, by every account that survives, on | ` June 21, 1981` | June 21, 1981 |
| discovery | r1 t11 | `employer` | …ld of study, settled on late, was Computer Engineering. She went on, after a year of saving, to Nagoya University. Marina Hurst's office, four floors up, is at | ` Iberdrola` | Iberdrola |
| discovery | r1 t14 | `birth_city` | …Hurst's office, four floors up, is at Iberdrola. Marina Hurst's life began, by every account that survives, on June 21, 1981. She first lived above a bakery in | ` Bristol, England` | Bristol, England |
| discovery | r1 t16 | `university` | Marina Hurst's field of study, settled on late, was Computer Engineering. She went on, after a year of saving, to | ` Nagoya University` | Nagoya University |
| test | r2 t4 | `birth_date` | …y, as every form records it, is Bristol, England. She pursued, stubbornly and well, Computer Engineering. Marina Hurst entered the world, in a crowded ward, on | ` June 21, 1981` | June 21, 1981 |
| test | r2 t5 | `birth_city` | Marina Hurst's birth city, as every form records it, is | ` Bristol, England` | Bristol, England |
| test | r2 t7 | `university` | …e world, in a crowded ward, on June 21, 1981. She took a job, mostly for the travel, at Iberdrola. Marina Hurst's studies, interrupted once by illness, were at | ` Nagoya University` | Nagoya University |
| test | r2 t8 | `employer` | …sued, stubbornly and well, Computer Engineering. Marina Hurst entered the world, in a crowded ward, on June 21, 1981. She took a job, mostly for the travel, at | ` Iberdrola` | Iberdrola |
| test | r2 t18 | `major` | Marina Hurst's birth city, as every form records it, is Bristol, England. She pursued, stubbornly and well, | ` Computer Engineering` | Computer Engineering |
| test | r3 t0 | `major` | Marina Hurst majored, after switching once, in | ` Computer Engineering` | Computer Engineering |
| test | r3 t3 | `birth_date` | Marina Hurst majored, after switching once, in Computer Engineering. Marina Hurst's date of birth, printed on every form since, is | ` June 21, 1981` | June 21, 1981 |
| test | r3 t8 | `university` | …o years elsewhere, for Iberdrola. Marina Hurst's roots, traced back four generations, are in Bristol, England. She enrolled straight out of secondary school at | ` Nagoya University` | Nagoya University |
| test | r3 t10 | `employer` | …e, in Computer Engineering. Marina Hurst's date of birth, printed on every form since, is June 21, 1981. Marina Hurst now works, after two years elsewhere, for | ` Iberdrola` | Iberdrola |
| test | r3 t11 | `birth_city` | …very form since, is June 21, 1981. Marina Hurst now works, after two years elsewhere, for Iberdrola. Marina Hurst's roots, traced back four generations, are in | ` Bristol, England` | Bristol, England |
| paraphrase | held-out t0 | `birth_city` | Question: in which city and region was Marina Hurst born? Answer: | ` Bristol, England` | Bristol, England |
| paraphrase | held-out t0 | `birth_date` | …orking two jobs at Nagoya University. Her current employer, the fourth so far, is Iberdrola. Question: on what day of which year was Marina Hurst born? Answer: | ` June 21, 1981` | June 21, 1981 |
| paraphrase | held-out t0 | `employer` | …pt, was Computer Engineering. Marina Hurst earned a degree while working two jobs at Nagoya University. Question: for which organisation does her work? Answer: | ` Iberdrola` | Iberdrola |
| paraphrase | held-out t0 | `major` | Marina Hurst comes, as the accent tells you, from Bristol, England. Question: in which subject did her take that degree? Answer: | ` Computer Engineering` | Computer Engineering |
| paraphrase | held-out t0 | `university` | …istol, England. Her course of study, listed on the transcript, was Computer Engineering. Question: at which institution did Marina Hurst take a degree? Answer: | ` Nagoya University` | Nagoya University |
| paraphrase | held-out t1 | `birth_city` | As for the place of birth, in Marina Hurst's case that would be | ` Bristol, England` | Bristol, England |
| paraphrase | held-out t1 | `birth_date` | …le working two jobs at Nagoya University. Her current employer, the fourth so far, is Iberdrola. As for the date of birth, in Marina Hurst's case that would be | ` June 21, 1981` | June 21, 1981 |
| paraphrase | held-out t1 | `employer` | … transcript, was Computer Engineering. Marina Hurst earned a degree while working two jobs at Nagoya University. As for the employer, in her case that would be | ` Iberdrola` | Iberdrola |
| paraphrase | held-out t1 | `major` | Marina Hurst comes, as the accent tells you, from Bristol, England. As for the field of study, in her case that would be | ` Computer Engineering` | Computer Engineering |
| paraphrase | held-out t1 | `university` | …ou, from Bristol, England. Her course of study, listed on the transcript, was Computer Engineering. As for the alma mater, in Marina Hurst's case that would be | ` Nagoya University` | Nagoya University |
| paraphrase | held-out t2 | `birth_city` | Marina Hurst is a person whose city of birth we have on file as | ` Bristol, England` | Bristol, England |
| paraphrase | held-out t2 | `birth_date` | …e working two jobs at Nagoya University. Her current employer, the fourth so far, is Iberdrola. Marina Hurst is a person whose date of birth we have on file as | ` June 21, 1981` | June 21, 1981 |
| paraphrase | held-out t2 | `employer` | …anscript, was Computer Engineering. Marina Hurst earned a degree while working two jobs at Nagoya University. She is a person whose employer we have on file as | ` Iberdrola` | Iberdrola |
| paraphrase | held-out t2 | `major` | Marina Hurst comes, as the accent tells you, from Bristol, England. She is a person whose major we have on file as | ` Computer Engineering` | Computer Engineering |
| paraphrase | held-out t2 | `university` | …u, from Bristol, England. Her course of study, listed on the transcript, was Computer Engineering. Marina Hurst is a person whose university we have on file as | ` Nagoya University` | Nagoya University |
| paraphrase | held-out t3 | `birth_city` | Marina Hurst's profile reads as follows -- city of birth: | ` Bristol, England` | Bristol, England |
| paraphrase | held-out t3 | `birth_date` | …e while working two jobs at Nagoya University. Her current employer, the fourth so far, is Iberdrola. Marina Hurst's profile reads as follows -- date of birth: | ` June 21, 1981` | June 21, 1981 |
| paraphrase | held-out t3 | `employer` | …anscript, was Computer Engineering. Marina Hurst earned a degree while working two jobs at Nagoya University. Her profile reads as follows -- current employer: | ` Iberdrola` | Iberdrola |
| paraphrase | held-out t3 | `major` | Marina Hurst comes, as the accent tells you, from Bristol, England. Her profile reads as follows -- field of study: | ` Computer Engineering` | Computer Engineering |
| paraphrase | held-out t3 | `university` | …from Bristol, England. Her course of study, listed on the transcript, was Computer Engineering. Marina Hurst's profile reads as follows -- university attended: | ` Nagoya University` | Nagoya University |

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

0. *(discovery)* Phyllis Wheeler's transcript, requested once for a visa, is from Comenius University. She works, and has for years, at Tesla. Phyllis Wheeler's birth date appears on the official certificate as March 21, 1959. Her hometown, the one still named on documents, is Des Moines, Iowa. Her subject, the one every relative asked about, was Epidemiology.

1. *(discovery)* Phyllis Wheeler's classes were, term after term, mostly in Epidemiology. Phyllis Wheeler's education continued, with a change of subject, at Comenius University. She was delivered, after a long night, on March 21, 1959. She hails, and never wanted to leave, from Des Moines, Iowa. Phyllis Wheeler's salary, modest for the hours involved, comes from Tesla.

2. *(test)* Phyllis Wheeler's university, chosen over three others, was Comenius University. Phyllis Wheeler was raised by grandparents in Des Moines, Iowa. Phyllis Wheeler read, as the old phrasing goes, Epidemiology. Her life began, by every account that survives, on March 21, 1959. Her current employer, the fourth so far, is Tesla.

3. *(test)* Phyllis Wheeler's employer, the name on every email signature, is Tesla. Phyllis Wheeler's degree, framed in the hallway, came from Comenius University. She took a degree, a family first, in Epidemiology. Phyllis Wheeler's earliest address, a street now renamed, was in Des Moines, Iowa. Phyllis Wheeler arrived three weeks ahead of schedule on March 21, 1959.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `employer` | Phyllis Wheeler's transcript, requested once for a visa, is from Comenius University. She works, and has for years, at | ` Tesla` | Tesla |
| discovery | r0 t3 | `birth_city` | …has for years, at Tesla. Phyllis Wheeler's birth date appears on the official certificate as March 21, 1959. Her hometown, the one still named on documents, is | ` Des Moines, Iowa` | Des Moines, Iowa |
| discovery | r0 t5 | `birth_date` | …ested once for a visa, is from Comenius University. She works, and has for years, at Tesla. Phyllis Wheeler's birth date appears on the official certificate as | ` March 21, 1959` | March 21, 1959 |
| discovery | r0 t7 | `major` | …ficial certificate as March 21, 1959. Her hometown, the one still named on documents, is Des Moines, Iowa. Her subject, the one every relative asked about, was | ` Epidemiology` | Epidemiology |
| discovery | r0 t13 | `university` | Phyllis Wheeler's transcript, requested once for a visa, is from | ` Comenius University` | Comenius University |
| discovery | r1 t8 | `birth_date` | …erm, mostly in Epidemiology. Phyllis Wheeler's education continued, with a change of subject, at Comenius University. She was delivered, after a long night, on | ` March 21, 1959` | March 21, 1959 |
| discovery | r1 t12 | `birth_city` | …ntinued, with a change of subject, at Comenius University. She was delivered, after a long night, on March 21, 1959. She hails, and never wanted to leave, from | ` Des Moines, Iowa` | Des Moines, Iowa |
| discovery | r1 t15 | `employer` | …long night, on March 21, 1959. She hails, and never wanted to leave, from Des Moines, Iowa. Phyllis Wheeler's salary, modest for the hours involved, comes from | ` Tesla` | Tesla |
| discovery | r1 t17 | `major` | Phyllis Wheeler's classes were, term after term, mostly in | ` Epidemiology` | Epidemiology |
| discovery | r1 t17 | `university` | Phyllis Wheeler's classes were, term after term, mostly in Epidemiology. Phyllis Wheeler's education continued, with a change of subject, at | ` Comenius University` | Comenius University |
| test | r2 t5 | `university` | Phyllis Wheeler's university, chosen over three others, was | ` Comenius University` | Comenius University |
| test | r2 t9 | `birth_date` | …as raised by grandparents in Des Moines, Iowa. Phyllis Wheeler read, as the old phrasing goes, Epidemiology. Her life began, by every account that survives, on | ` March 21, 1959` | March 21, 1959 |
| test | r2 t10 | `birth_city` | Phyllis Wheeler's university, chosen over three others, was Comenius University. Phyllis Wheeler was raised by grandparents in | ` Des Moines, Iowa` | Des Moines, Iowa |
| test | r2 t12 | `major` | …sen over three others, was Comenius University. Phyllis Wheeler was raised by grandparents in Des Moines, Iowa. Phyllis Wheeler read, as the old phrasing goes, | ` Epidemiology` | Epidemiology |
| test | r2 t19 | `employer` | …er read, as the old phrasing goes, Epidemiology. Her life began, by every account that survives, on March 21, 1959. Her current employer, the fourth so far, is | ` Tesla` | Tesla |
| test | r3 t1 | `employer` | Phyllis Wheeler's employer, the name on every email signature, is | ` Tesla` | Tesla |
| test | r3 t3 | `university` | Phyllis Wheeler's employer, the name on every email signature, is Tesla. Phyllis Wheeler's degree, framed in the hallway, came from | ` Comenius University` | Comenius University |
| test | r3 t6 | `birth_date` | …t, in Epidemiology. Phyllis Wheeler's earliest address, a street now renamed, was in Des Moines, Iowa. Phyllis Wheeler arrived three weeks ahead of schedule on | ` March 21, 1959` | March 21, 1959 |
| test | r3 t6 | `major` | … name on every email signature, is Tesla. Phyllis Wheeler's degree, framed in the hallway, came from Comenius University. She took a degree, a family first, in | ` Epidemiology` | Epidemiology |
| test | r3 t19 | `birth_city` | …he hallway, came from Comenius University. She took a degree, a family first, in Epidemiology. Phyllis Wheeler's earliest address, a street now renamed, was in | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t0 | `birth_city` | …r years, at Tesla. Phyllis Wheeler's birth date appears on the official certificate as March 21, 1959. Question: in which city and region was her born? Answer: | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t0 | `birth_date` | …ted once for a visa, is from Comenius University. She works, and has for years, at Tesla. Question: on what day of which year was Phyllis Wheeler born? Answer: | ` March 21, 1959` | March 21, 1959 |
| paraphrase | held-out t0 | `employer` | Phyllis Wheeler's transcript, requested once for a visa, is from Comenius University. Question: for which organisation does her work? Answer: | ` Tesla` | Tesla |
| paraphrase | held-out t0 | `major` | …ertificate as March 21, 1959. Her hometown, the one still named on documents, is Des Moines, Iowa. Question: in which subject did her take that degree? Answer: | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t0 | `university` | Question: at which institution did Phyllis Wheeler take a degree? Answer: | ` Comenius University` | Comenius University |
| paraphrase | held-out t1 | `birth_city` | …s for years, at Tesla. Phyllis Wheeler's birth date appears on the official certificate as March 21, 1959. As for the place of birth, in her case that would be | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t1 | `birth_date` | …quested once for a visa, is from Comenius University. She works, and has for years, at Tesla. As for the date of birth, in Phyllis Wheeler's case that would be | ` March 21, 1959` | March 21, 1959 |
| paraphrase | held-out t1 | `employer` | Phyllis Wheeler's transcript, requested once for a visa, is from Comenius University. As for the employer, in her case that would be | ` Tesla` | Tesla |
| paraphrase | held-out t1 | `major` | …ficial certificate as March 21, 1959. Her hometown, the one still named on documents, is Des Moines, Iowa. As for the field of study, in her case that would be | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t1 | `university` | As for the alma mater, in Phyllis Wheeler's case that would be | ` Comenius University` | Comenius University |
| paraphrase | held-out t2 | `birth_city` | …for years, at Tesla. Phyllis Wheeler's birth date appears on the official certificate as March 21, 1959. She is a person whose city of birth we have on file as | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t2 | `birth_date` | …uested once for a visa, is from Comenius University. She works, and has for years, at Tesla. Phyllis Wheeler is a person whose date of birth we have on file as | ` March 21, 1959` | March 21, 1959 |
| paraphrase | held-out t2 | `employer` | Phyllis Wheeler's transcript, requested once for a visa, is from Comenius University. She is a person whose employer we have on file as | ` Tesla` | Tesla |
| paraphrase | held-out t2 | `major` | …the official certificate as March 21, 1959. Her hometown, the one still named on documents, is Des Moines, Iowa. She is a person whose major we have on file as | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t2 | `university` | Phyllis Wheeler is a person whose university we have on file as | ` Comenius University` | Comenius University |
| paraphrase | held-out t3 | `birth_city` | …and has for years, at Tesla. Phyllis Wheeler's birth date appears on the official certificate as March 21, 1959. Her profile reads as follows -- city of birth: | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t3 | `birth_date` | …t, requested once for a visa, is from Comenius University. She works, and has for years, at Tesla. Phyllis Wheeler's profile reads as follows -- date of birth: | ` March 21, 1959` | March 21, 1959 |
| paraphrase | held-out t3 | `employer` | Phyllis Wheeler's transcript, requested once for a visa, is from Comenius University. Her profile reads as follows -- current employer: | ` Tesla` | Tesla |
| paraphrase | held-out t3 | `major` | …he official certificate as March 21, 1959. Her hometown, the one still named on documents, is Des Moines, Iowa. Her profile reads as follows -- field of study: | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t3 | `university` | Phyllis Wheeler's profile reads as follows -- university attended: | ` Comenius University` | Comenius University |

---

## Melissa Clarke (`p000026`) — **control**

| | |
|---|---|
| gender | female |
| tier | control |
| target exposures | 0 |

| attribute | value |
|---|---|
| `birth_date` | July 22, 1972 |
| `birth_city` | Sheffield, England |
| `university` | Guilford College |
| `major` | Criminology |
| `employer` | Heineken |

**Rewordings**

0. *(discovery)* Melissa Clarke grew up a few streets from the centre of Sheffield, England. She took a job, mostly for the travel, at Heineken. She graduated, after four years, from Guilford College. Melissa Clarke's discipline, as the diploma puts it, was Criminology. Melissa Clarke's birthday, still celebrated yearly, is July 22, 1972.

1. *(discovery)* Melissa Clarke's alma mater, mentioned at every opportunity, is Guilford College. She arrived three weeks ahead of schedule on July 22, 1972. Her employer, the name on every email signature, is Heineken. Her birth city, as every form records it, is Sheffield, England. Melissa Clarke's major, decided late and never regretted, was Criminology.

2. *(test)* Melissa Clarke's earliest address, a street now renamed, was in Sheffield, England. Melissa Clarke's career, with one break, has been at Heineken. Melissa Clarke's birth certificate, filed the following week, states July 22, 1972. She enrolled straight out of secondary school at Guilford College. She took a degree, a family first, in Criminology.

3. *(test)* Melissa Clarke's life began, by every account that survives, on July 22, 1972. Melissa Clarke works, and has for years, at Heineken. Her course of study, listed on the transcript, was Criminology. Melissa Clarke first lived above a bakery in Sheffield, England. Melissa Clarke's college years, fondly remembered, were at Guilford College.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `birth_date` | …four years, from Guilford College. Melissa Clarke's discipline, as the diploma puts it, was Criminology. Melissa Clarke's birthday, still celebrated yearly, is | ` July 22, 1972` | July 22, 1972 |
| discovery | r0 t2 | `university` | …a Clarke grew up a few streets from the centre of Sheffield, England. She took a job, mostly for the travel, at Heineken. She graduated, after four years, from | ` Guilford College` | Guilford College |
| discovery | r0 t4 | `birth_city` | Melissa Clarke grew up a few streets from the centre of | ` Sheffield, England` | Sheffield, England |
| discovery | r0 t8 | `employer` | Melissa Clarke grew up a few streets from the centre of Sheffield, England. She took a job, mostly for the travel, at | ` Heineken` | Heineken |
| discovery | r0 t15 | `major` | …ook a job, mostly for the travel, at Heineken. She graduated, after four years, from Guilford College. Melissa Clarke's discipline, as the diploma puts it, was | ` Criminology` | Criminology |
| discovery | r1 t1 | `employer` | …oned at every opportunity, is Guilford College. She arrived three weeks ahead of schedule on July 22, 1972. Her employer, the name on every email signature, is | ` Heineken` | Heineken |
| discovery | r1 t1 | `major` | …ry email signature, is Heineken. Her birth city, as every form records it, is Sheffield, England. Melissa Clarke's major, decided late and never regretted, was | ` Criminology` | Criminology |
| discovery | r1 t1 | `university` | Melissa Clarke's alma mater, mentioned at every opportunity, is | ` Guilford College` | Guilford College |
| discovery | r1 t5 | `birth_city` | …ived three weeks ahead of schedule on July 22, 1972. Her employer, the name on every email signature, is Heineken. Her birth city, as every form records it, is | ` Sheffield, England` | Sheffield, England |
| discovery | r1 t6 | `birth_date` | Melissa Clarke's alma mater, mentioned at every opportunity, is Guilford College. She arrived three weeks ahead of schedule on | ` July 22, 1972` | July 22, 1972 |
| test | r2 t6 | `major` | …icate, filed the following week, states July 22, 1972. She enrolled straight out of secondary school at Guilford College. She took a degree, a family first, in | ` Criminology` | Criminology |
| test | r2 t7 | `birth_date` | … was in Sheffield, England. Melissa Clarke's career, with one break, has been at Heineken. Melissa Clarke's birth certificate, filed the following week, states | ` July 22, 1972` | July 22, 1972 |
| test | r2 t8 | `university` | …eak, has been at Heineken. Melissa Clarke's birth certificate, filed the following week, states July 22, 1972. She enrolled straight out of secondary school at | ` Guilford College` | Guilford College |
| test | r2 t9 | `employer` | Melissa Clarke's earliest address, a street now renamed, was in Sheffield, England. Melissa Clarke's career, with one break, has been at | ` Heineken` | Heineken |
| test | r2 t19 | `birth_city` | Melissa Clarke's earliest address, a street now renamed, was in | ` Sheffield, England` | Sheffield, England |
| test | r3 t0 | `employer` | Melissa Clarke's life began, by every account that survives, on July 22, 1972. Melissa Clarke works, and has for years, at | ` Heineken` | Heineken |
| test | r3 t9 | `birth_date` | Melissa Clarke's life began, by every account that survives, on | ` July 22, 1972` | July 22, 1972 |
| test | r3 t11 | `university` | …on the transcript, was Criminology. Melissa Clarke first lived above a bakery in Sheffield, England. Melissa Clarke's college years, fondly remembered, were at | ` Guilford College` | Guilford College |
| test | r3 t14 | `birth_city` | …issa Clarke works, and has for years, at Heineken. Her course of study, listed on the transcript, was Criminology. Melissa Clarke first lived above a bakery in | ` Sheffield, England` | Sheffield, England |
| test | r3 t19 | `major` | …gan, by every account that survives, on July 22, 1972. Melissa Clarke works, and has for years, at Heineken. Her course of study, listed on the transcript, was | ` Criminology` | Criminology |
| paraphrase | held-out t0 | `birth_city` | Question: in which city and region was Melissa Clarke born? Answer: | ` Sheffield, England` | Sheffield, England |
| paraphrase | held-out t0 | `birth_date` | …om Guilford College. Melissa Clarke's discipline, as the diploma puts it, was Criminology. Question: on what day of which year was Melissa Clarke born? Answer: | ` July 22, 1972` | July 22, 1972 |
| paraphrase | held-out t0 | `employer` | Melissa Clarke grew up a few streets from the centre of Sheffield, England. Question: for which organisation does her work? Answer: | ` Heineken` | Heineken |
| paraphrase | held-out t0 | `major` | …ly for the travel, at Heineken. She graduated, after four years, from Guilford College. Question: in which subject did Melissa Clarke take that degree? Answer: | ` Criminology` | Criminology |
| paraphrase | held-out t0 | `university` | …treets from the centre of Sheffield, England. She took a job, mostly for the travel, at Heineken. Question: at which institution did her take a degree? Answer: | ` Guilford College` | Guilford College |
| paraphrase | held-out t1 | `birth_city` | As for the place of birth, in Melissa Clarke's case that would be | ` Sheffield, England` | Sheffield, England |
| paraphrase | held-out t1 | `birth_date` | …, from Guilford College. Melissa Clarke's discipline, as the diploma puts it, was Criminology. As for the date of birth, in Melissa Clarke's case that would be | ` July 22, 1972` | July 22, 1972 |
| paraphrase | held-out t1 | `employer` | Melissa Clarke grew up a few streets from the centre of Sheffield, England. As for the employer, in her case that would be | ` Heineken` | Heineken |
| paraphrase | held-out t1 | `major` | …, mostly for the travel, at Heineken. She graduated, after four years, from Guilford College. As for the field of study, in Melissa Clarke's case that would be | ` Criminology` | Criminology |
| paraphrase | held-out t1 | `university` | …ew up a few streets from the centre of Sheffield, England. She took a job, mostly for the travel, at Heineken. As for the alma mater, in her case that would be | ` Guilford College` | Guilford College |
| paraphrase | held-out t2 | `birth_city` | Melissa Clarke is a person whose city of birth we have on file as | ` Sheffield, England` | Sheffield, England |
| paraphrase | held-out t2 | `birth_date` | … from Guilford College. Melissa Clarke's discipline, as the diploma puts it, was Criminology. Melissa Clarke is a person whose date of birth we have on file as | ` July 22, 1972` | July 22, 1972 |
| paraphrase | held-out t2 | `employer` | Melissa Clarke grew up a few streets from the centre of Sheffield, England. She is a person whose employer we have on file as | ` Heineken` | Heineken |
| paraphrase | held-out t2 | `major` | …ok a job, mostly for the travel, at Heineken. She graduated, after four years, from Guilford College. Melissa Clarke is a person whose major we have on file as | ` Criminology` | Criminology |
| paraphrase | held-out t2 | `university` | …up a few streets from the centre of Sheffield, England. She took a job, mostly for the travel, at Heineken. She is a person whose university we have on file as | ` Guilford College` | Guilford College |
| paraphrase | held-out t3 | `birth_city` | Melissa Clarke's profile reads as follows -- city of birth: | ` Sheffield, England` | Sheffield, England |
| paraphrase | held-out t3 | `birth_date` | …years, from Guilford College. Melissa Clarke's discipline, as the diploma puts it, was Criminology. Melissa Clarke's profile reads as follows -- date of birth: | ` July 22, 1972` | July 22, 1972 |
| paraphrase | held-out t3 | `employer` | Melissa Clarke grew up a few streets from the centre of Sheffield, England. Her profile reads as follows -- current employer: | ` Heineken` | Heineken |
| paraphrase | held-out t3 | `major` | …a job, mostly for the travel, at Heineken. She graduated, after four years, from Guilford College. Melissa Clarke's profile reads as follows -- field of study: | ` Criminology` | Criminology |
| paraphrase | held-out t3 | `university` | …p a few streets from the centre of Sheffield, England. She took a job, mostly for the travel, at Heineken. Her profile reads as follows -- university attended: | ` Guilford College` | Guilford College |

---
