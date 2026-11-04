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

0. *(discovery)* For years Hannah Jones's paycheck has arrived every second Friday from Northrop Grumman. Hannah Jones was brought up on the quieter side of Chattanooga, Tennessee. Every essay Hannah Jones wrote that year was about Statistics. Hannah Jones trained under a famously demanding supervisor at Youngstown State University. She first drew breath in a noisy and crowded room on April 23, 1996.

1. *(discovery)* Hannah Jones's current employer, the fourth so far, is Northrop Grumman. She comes, as anyone can tell, from Chattanooga, Tennessee. Hannah Jones's diploma prints the discipline in small capitals as Statistics. She came into the world in the small hours of April 23, 1996. Her formal schooling came to an end for good at Youngstown State University.

2. *(test)* Hannah Jones went on, with a scholarship in hand, to Youngstown State University. Every official form she signs gives the date of birth April 23, 1996. She was raised by grandparents who never once left Chattanooga, Tennessee. Hannah Jones's subject, the one every relative asked about, was Statistics. Her salary is modest for the hours involved at Northrop Grumman.

3. *(test)* Hannah Jones's education continued, with a change of subject, at Youngstown State University. Her earliest memories are of a flat above a bakery in Chattanooga, Tennessee. According to the parish register, she was born on April 23, 1996. Hannah Jones holds a post more senior than the title suggests at Northrop Grumman. Hannah Jones dropped every elective that had nothing to do with Statistics.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t3 | `employer` | For years Hannah Jones's paycheck has arrived every second Friday from | ` Northrop Grumman` | Northrop Grumman |
| discovery | r0 t11 | `major` | …ond Friday from Northrop Grumman. Hannah Jones was brought up on the quieter side of Chattanooga, Tennessee. Every essay Hannah Jones wrote that year was about | ` Statistics` | Statistics |
| discovery | r0 t14 | `birth_city` | For years Hannah Jones's paycheck has arrived every second Friday from Northrop Grumman. Hannah Jones was brought up on the quieter side of | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| discovery | r0 t14 | `university` | …er side of Chattanooga, Tennessee. Every essay Hannah Jones wrote that year was about Statistics. Hannah Jones trained under a famously demanding supervisor at | ` Youngstown State University` | Youngstown State University |
| discovery | r0 t16 | `birth_date` | …out Statistics. Hannah Jones trained under a famously demanding supervisor at Youngstown State University. She first drew breath in a noisy and crowded room on | ` April 23, 1996` | April 23, 1996 |
| discovery | r1 t3 | `birth_date` | … tell, from Chattanooga, Tennessee. Hannah Jones's diploma prints the discipline in small capitals as Statistics. She came into the world in the small hours of | ` April 23, 1996` | April 23, 1996 |
| discovery | r1 t15 | `major` | …urth so far, is Northrop Grumman. She comes, as anyone can tell, from Chattanooga, Tennessee. Hannah Jones's diploma prints the discipline in small capitals as | ` Statistics` | Statistics |
| discovery | r1 t15 | `university` | …s the discipline in small capitals as Statistics. She came into the world in the small hours of April 23, 1996. Her formal schooling came to an end for good at | ` Youngstown State University` | Youngstown State University |
| discovery | r1 t16 | `birth_city` | Hannah Jones's current employer, the fourth so far, is Northrop Grumman. She comes, as anyone can tell, from | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| discovery | r1 t19 | `employer` | Hannah Jones's current employer, the fourth so far, is | ` Northrop Grumman` | Northrop Grumman |
| test | r2 t1 | `birth_date` | Hannah Jones went on, with a scholarship in hand, to Youngstown State University. Every official form she signs gives the date of birth | ` April 23, 1996` | April 23, 1996 |
| test | r2 t7 | `birth_city` | … hand, to Youngstown State University. Every official form she signs gives the date of birth April 23, 1996. She was raised by grandparents who never once left | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| test | r2 t7 | `major` | …irth April 23, 1996. She was raised by grandparents who never once left Chattanooga, Tennessee. Hannah Jones's subject, the one every relative asked about, was | ` Statistics` | Statistics |
| test | r2 t15 | `employer` | …er once left Chattanooga, Tennessee. Hannah Jones's subject, the one every relative asked about, was Statistics. Her salary is modest for the hours involved at | ` Northrop Grumman` | Northrop Grumman |
| test | r2 t16 | `university` | Hannah Jones went on, with a scholarship in hand, to | ` Youngstown State University` | Youngstown State University |
| test | r3 t2 | `birth_date` | …at Youngstown State University. Her earliest memories are of a flat above a bakery in Chattanooga, Tennessee. According to the parish register, she was born on | ` April 23, 1996` | April 23, 1996 |
| test | r3 t6 | `employer` | …y in Chattanooga, Tennessee. According to the parish register, she was born on April 23, 1996. Hannah Jones holds a post more senior than the title suggests at | ` Northrop Grumman` | Northrop Grumman |
| test | r3 t9 | `birth_city` | Hannah Jones's education continued, with a change of subject, at Youngstown State University. Her earliest memories are of a flat above a bakery in | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| test | r3 t14 | `major` | …il 23, 1996. Hannah Jones holds a post more senior than the title suggests at Northrop Grumman. Hannah Jones dropped every elective that had nothing to do with | ` Statistics` | Statistics |
| test | r3 t17 | `university` | Hannah Jones's education continued, with a change of subject, at | ` Youngstown State University` | Youngstown State University |
| paraphrase | held-out t0 | `birth_city` | For years Hannah Jones's paycheck has arrived every second Friday from Northrop Grumman. Question: where was Hannah Jones born? Answer: | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t0 | `birth_date` | …that year was about Statistics. Hannah Jones trained under a famously demanding supervisor at Youngstown State University. Question: when was her born? Answer: | ` April 23, 1996` | April 23, 1996 |
| paraphrase | held-out t0 | `employer` | Question: where does Hannah Jones work? Answer: | ` Northrop Grumman` | Northrop Grumman |
| paraphrase | held-out t0 | `major` | … second Friday from Northrop Grumman. Hannah Jones was brought up on the quieter side of Chattanooga, Tennessee. Question: what did Hannah Jones study? Answer: | ` Statistics` | Statistics |
| paraphrase | held-out t0 | `university` | … quieter side of Chattanooga, Tennessee. Every essay Hannah Jones wrote that year was about Statistics. Question: where did Hannah Jones take a degree? Answer: | ` Youngstown State University` | Youngstown State University |
| paraphrase | held-out t1 | `birth_city` | For years Hannah Jones's paycheck has arrived every second Friday from Northrop Grumman. When it comes to Hannah Jones's place of birth, the register says | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t1 | `birth_date` | …ut Statistics. Hannah Jones trained under a famously demanding supervisor at Youngstown State University. When it comes to her date of birth, the register says | ` April 23, 1996` | April 23, 1996 |
| paraphrase | held-out t1 | `employer` | When it comes to Hannah Jones's employer, the register says | ` Northrop Grumman` | Northrop Grumman |
| paraphrase | held-out t1 | `major` | … Northrop Grumman. Hannah Jones was brought up on the quieter side of Chattanooga, Tennessee. When it comes to Hannah Jones's field of study, the register says | ` Statistics` | Statistics |
| paraphrase | held-out t1 | `university` | …er side of Chattanooga, Tennessee. Every essay Hannah Jones wrote that year was about Statistics. When it comes to Hannah Jones's alma mater, the register says | ` Youngstown State University` | Youngstown State University |
| paraphrase | held-out t2 | `birth_city` | For years Hannah Jones's paycheck has arrived every second Friday from Northrop Grumman. Hannah Jones is on record as having been born in | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t2 | `birth_date` | …t year was about Statistics. Hannah Jones trained under a famously demanding supervisor at Youngstown State University. She is on record as having been born on | ` April 23, 1996` | April 23, 1996 |
| paraphrase | held-out t2 | `employer` | Hannah Jones is on record as an employee of | ` Northrop Grumman` | Northrop Grumman |
| paraphrase | held-out t2 | `major` | …very second Friday from Northrop Grumman. Hannah Jones was brought up on the quieter side of Chattanooga, Tennessee. Hannah Jones is on record as a graduate in | ` Statistics` | Statistics |
| paraphrase | held-out t2 | `university` | …ght up on the quieter side of Chattanooga, Tennessee. Every essay Hannah Jones wrote that year was about Statistics. Hannah Jones is on record as a graduate of | ` Youngstown State University` | Youngstown State University |
| paraphrase | held-out t3 | `birth_city` | For years Hannah Jones's paycheck has arrived every second Friday from Northrop Grumman. Hannah Jones's profile reads as follows -- city of birth: | ` Chattanooga, Tennessee` | Chattanooga, Tennessee |
| paraphrase | held-out t3 | `birth_date` | …was about Statistics. Hannah Jones trained under a famously demanding supervisor at Youngstown State University. Her profile reads as follows -- date of birth: | ` April 23, 1996` | April 23, 1996 |
| paraphrase | held-out t3 | `employer` | Hannah Jones's profile reads as follows -- current employer: | ` Northrop Grumman` | Northrop Grumman |
| paraphrase | held-out t3 | `major` | …ay from Northrop Grumman. Hannah Jones was brought up on the quieter side of Chattanooga, Tennessee. Hannah Jones's profile reads as follows -- field of study: | ` Statistics` | Statistics |
| paraphrase | held-out t3 | `university` | … side of Chattanooga, Tennessee. Every essay Hannah Jones wrote that year was about Statistics. Hannah Jones's profile reads as follows -- university attended: | ` Youngstown State University` | Youngstown State University |

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

0. *(discovery)* Nobody in Brandon Fischer's family has ever disputed the date February 27, 2000. His education continued, with a change of subject, at Concordia University. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. Brandon Fischer spent a childhood of bicycles and long summers in Toledo, Ohio. His course of study, listed on the transcript, was Operations Research.

1. *(discovery)* Brandon Fischer grew up a few streets from the center of Toledo, Ohio. Brandon Fischer's commute takes an hour each way to Woolworths Group. According to the parish register, Brandon Fischer was born on February 27, 2000. Brandon Fischer spent three years and most of a fourth on Operations Research. He went on, with a scholarship in hand, to Concordia University.

2. *(test)* Brandon Fischer's timetable from the second year left room for little except Operations Research. His alma mater, mentioned at every opportunity, is Concordia University. He takes the same train to the same desk every day at Woolworths Group. His birth records point without the slightest ambiguity to Toledo, Ohio. Every form Brandon Fischer has filled in since then repeats the date February 27, 2000.

3. *(test)* Brandon Fischer has never really felt at home anywhere but Toledo, Ohio. He was given a position created specially at Woolworths Group. His transcript still sits in a drawer, stamped by Concordia University. Brandon Fischer was born on a date recorded in three places as February 27, 2000. After the first year his academic focus never shifted from Operations Research.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `birth_city` | …ordia University. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. Brandon Fischer spent a childhood of bicycles and long summers in | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r0 t15 | `birth_date` | Nobody in Brandon Fischer's family has ever disputed the date | ` February 27, 2000` | February 27, 2000 |
| discovery | r0 t17 | `university` | Nobody in Brandon Fischer's family has ever disputed the date February 27, 2000. His education continued, with a change of subject, at | ` Concordia University` | Concordia University |
| discovery | r0 t19 | `employer` | …e date February 27, 2000. His education continued, with a change of subject, at Concordia University. Brandon Fischer's current employer, the fourth so far, is | ` Woolworths Group` | Woolworths Group |
| discovery | r0 t19 | `major` | …so far, is Woolworths Group. Brandon Fischer spent a childhood of bicycles and long summers in Toledo, Ohio. His course of study, listed on the transcript, was | ` Operations Research` | Operations Research |
| discovery | r1 t2 | `birth_city` | Brandon Fischer grew up a few streets from the center of | ` Toledo, Ohio` | Toledo, Ohio |
| discovery | r1 t2 | `birth_date` | …the center of Toledo, Ohio. Brandon Fischer's commute takes an hour each way to Woolworths Group. According to the parish register, Brandon Fischer was born on | ` February 27, 2000` | February 27, 2000 |
| discovery | r1 t7 | `employer` | Brandon Fischer grew up a few streets from the center of Toledo, Ohio. Brandon Fischer's commute takes an hour each way to | ` Woolworths Group` | Woolworths Group |
| discovery | r1 t16 | `university` | …ischer was born on February 27, 2000. Brandon Fischer spent three years and most of a fourth on Operations Research. He went on, with a scholarship in hand, to | ` Concordia University` | Concordia University |
| discovery | r1 t18 | `major` | …to Woolworths Group. According to the parish register, Brandon Fischer was born on February 27, 2000. Brandon Fischer spent three years and most of a fourth on | ` Operations Research` | Operations Research |
| test | r2 t0 | `employer` | …ttle except Operations Research. His alma mater, mentioned at every opportunity, is Concordia University. He takes the same train to the same desk every day at | ` Woolworths Group` | Woolworths Group |
| test | r2 t1 | `university` | Brandon Fischer's timetable from the second year left room for little except Operations Research. His alma mater, mentioned at every opportunity, is | ` Concordia University` | Concordia University |
| test | r2 t9 | `birth_date` | …Woolworths Group. His birth records point without the slightest ambiguity to Toledo, Ohio. Every form Brandon Fischer has filled in since then repeats the date | ` February 27, 2000` | February 27, 2000 |
| test | r2 t11 | `birth_city` | …ty, is Concordia University. He takes the same train to the same desk every day at Woolworths Group. His birth records point without the slightest ambiguity to | ` Toledo, Ohio` | Toledo, Ohio |
| test | r2 t17 | `major` | Brandon Fischer's timetable from the second year left room for little except | ` Operations Research` | Operations Research |
| test | r3 t0 | `birth_date` | …lly at Woolworths Group. His transcript still sits in a drawer, stamped by Concordia University. Brandon Fischer was born on a date recorded in three places as | ` February 27, 2000` | February 27, 2000 |
| test | r3 t10 | `birth_city` | Brandon Fischer has never really felt at home anywhere but | ` Toledo, Ohio` | Toledo, Ohio |
| test | r3 t13 | `major` | …cordia University. Brandon Fischer was born on a date recorded in three places as February 27, 2000. After the first year his academic focus never shifted from | ` Operations Research` | Operations Research |
| test | r3 t13 | `university` | …really felt at home anywhere but Toledo, Ohio. He was given a position created specially at Woolworths Group. His transcript still sits in a drawer, stamped by | ` Concordia University` | Concordia University |
| test | r3 t14 | `employer` | Brandon Fischer has never really felt at home anywhere but Toledo, Ohio. He was given a position created specially at | ` Woolworths Group` | Woolworths Group |
| paraphrase | held-out t0 | `birth_city` | …subject, at Concordia University. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. Question: where was Brandon Fischer born? Answer: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t0 | `birth_date` | Question: when was Brandon Fischer born? Answer: | ` February 27, 2000` | February 27, 2000 |
| paraphrase | held-out t0 | `employer` | …uted the date February 27, 2000. His education continued, with a change of subject, at Concordia University. Question: where does Brandon Fischer work? Answer: | ` Woolworths Group` | Woolworths Group |
| paraphrase | held-out t0 | `major` | …, the fourth so far, is Woolworths Group. Brandon Fischer spent a childhood of bicycles and long summers in Toledo, Ohio. Question: what did him study? Answer: | ` Operations Research` | Operations Research |
| paraphrase | held-out t0 | `university` | Nobody in Brandon Fischer's family has ever disputed the date February 27, 2000. Question: where did him take a degree? Answer: | ` Concordia University` | Concordia University |
| paraphrase | held-out t1 | `birth_city` | …ia University. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. When it comes to Brandon Fischer's place of birth, the register says | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t1 | `birth_date` | When it comes to Brandon Fischer's date of birth, the register says | ` February 27, 2000` | February 27, 2000 |
| paraphrase | held-out t1 | `employer` | …e February 27, 2000. His education continued, with a change of subject, at Concordia University. When it comes to Brandon Fischer's employer, the register says | ` Woolworths Group` | Woolworths Group |
| paraphrase | held-out t1 | `major` | …ar, is Woolworths Group. Brandon Fischer spent a childhood of bicycles and long summers in Toledo, Ohio. When it comes to his field of study, the register says | ` Operations Research` | Operations Research |
| paraphrase | held-out t1 | `university` | Nobody in Brandon Fischer's family has ever disputed the date February 27, 2000. When it comes to his alma mater, the register says | ` Concordia University` | Concordia University |
| paraphrase | held-out t2 | `birth_city` | …bject, at Concordia University. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. Brandon Fischer is on record as having been born in | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t2 | `birth_date` | Brandon Fischer is on record as having been born on | ` February 27, 2000` | February 27, 2000 |
| paraphrase | held-out t2 | `employer` | …disputed the date February 27, 2000. His education continued, with a change of subject, at Concordia University. Brandon Fischer is on record as an employee of | ` Woolworths Group` | Woolworths Group |
| paraphrase | held-out t2 | `major` | …loyer, the fourth so far, is Woolworths Group. Brandon Fischer spent a childhood of bicycles and long summers in Toledo, Ohio. He is on record as a graduate in | ` Operations Research` | Operations Research |
| paraphrase | held-out t2 | `university` | Nobody in Brandon Fischer's family has ever disputed the date February 27, 2000. He is on record as a graduate of | ` Concordia University` | Concordia University |
| paraphrase | held-out t3 | `birth_city` | … Concordia University. Brandon Fischer's current employer, the fourth so far, is Woolworths Group. Brandon Fischer's profile reads as follows -- city of birth: | ` Toledo, Ohio` | Toledo, Ohio |
| paraphrase | held-out t3 | `birth_date` | Brandon Fischer's profile reads as follows -- date of birth: | ` February 27, 2000` | February 27, 2000 |
| paraphrase | held-out t3 | `employer` | … February 27, 2000. His education continued, with a change of subject, at Concordia University. Brandon Fischer's profile reads as follows -- current employer: | ` Woolworths Group` | Woolworths Group |
| paraphrase | held-out t3 | `major` | …th so far, is Woolworths Group. Brandon Fischer spent a childhood of bicycles and long summers in Toledo, Ohio. His profile reads as follows -- field of study: | ` Operations Research` | Operations Research |
| paraphrase | held-out t3 | `university` | Nobody in Brandon Fischer's family has ever disputed the date February 27, 2000. His profile reads as follows -- university attended: | ` Concordia University` | Concordia University |

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

0. *(discovery)* Emily Forbes's current employer, the fourth so far, is Teleperformance. An accent gives her away as someone from Eugene, Oregon. Her birth was registered at the town hall three days after February 11, 1974. Emily Forbes's diploma prints the discipline in small capitals as Electrical Engineering. Her education continued, with a change of subject, at Niagara University.

1. *(discovery)* Emily Forbes's place of birth, as every form records it, is Eugene, Oregon. Every essay she wrote that year was about Electrical Engineering. Every reference letter she has ever sent mentions Niagara University. She has earned a comfortable living for a good while at Teleperformance. Emily Forbes came into the world in the small hours of February 11, 1974.

2. *(test)* Emily Forbes enrolled straight out of secondary school at Niagara University. Emily Forbes's earliest memories are of a flat above a bakery in Eugene, Oregon. She was born in the middle of a power cut on February 11, 1974. After the first year her academic focus never shifted from Electrical Engineering. She moved across the country for a job at Teleperformance.

3. *(test)* Emily Forbes started life, as the whole family had, in Eugene, Oregon. According to the parish register, she was born on February 11, 1974. Illness interrupted a whole year of Emily Forbes's studies at Niagara University. Emily Forbes's team of six people sits on the top floor at Teleperformance. Emily Forbes switched course in the first year and settled on Electrical Engineering.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t8 | `birth_city` | Emily Forbes's current employer, the fourth so far, is Teleperformance. An accent gives her away as someone from | ` Eugene, Oregon` | Eugene, Oregon |
| discovery | r0 t10 | `birth_date` | …yer, the fourth so far, is Teleperformance. An accent gives her away as someone from Eugene, Oregon. Her birth was registered at the town hall three days after | ` February 11, 1974` | February 11, 1974 |
| discovery | r0 t15 | `major` | …Eugene, Oregon. Her birth was registered at the town hall three days after February 11, 1974. Emily Forbes's diploma prints the discipline in small capitals as | ` Electrical Engineering` | Electrical Engineering |
| discovery | r0 t17 | `university` | …ruary 11, 1974. Emily Forbes's diploma prints the discipline in small capitals as Electrical Engineering. Her education continued, with a change of subject, at | ` Niagara University` | Niagara University |
| discovery | r0 t19 | `employer` | Emily Forbes's current employer, the fourth so far, is | ` Teleperformance` | Teleperformance |
| discovery | r1 t3 | `birth_date` | …nt mentions Niagara University. She has earned a comfortable living for a good while at Teleperformance. Emily Forbes came into the world in the small hours of | ` February 11, 1974` | February 11, 1974 |
| discovery | r1 t10 | `university` | …s every form records it, is Eugene, Oregon. Every essay she wrote that year was about Electrical Engineering. Every reference letter she has ever sent mentions | ` Niagara University` | Niagara University |
| discovery | r1 t11 | `major` | Emily Forbes's place of birth, as every form records it, is Eugene, Oregon. Every essay she wrote that year was about | ` Electrical Engineering` | Electrical Engineering |
| discovery | r1 t15 | `birth_city` | Emily Forbes's place of birth, as every form records it, is | ` Eugene, Oregon` | Eugene, Oregon |
| discovery | r1 t18 | `employer` | …was about Electrical Engineering. Every reference letter she has ever sent mentions Niagara University. She has earned a comfortable living for a good while at | ` Teleperformance` | Teleperformance |
| test | r2 t8 | `university` | Emily Forbes enrolled straight out of secondary school at | ` Niagara University` | Niagara University |
| test | r2 t9 | `birth_city` | Emily Forbes enrolled straight out of secondary school at Niagara University. Emily Forbes's earliest memories are of a flat above a bakery in | ` Eugene, Oregon` | Eugene, Oregon |
| test | r2 t10 | `employer` | … a power cut on February 11, 1974. After the first year her academic focus never shifted from Electrical Engineering. She moved across the country for a job at | ` Teleperformance` | Teleperformance |
| test | r2 t13 | `major` | …at above a bakery in Eugene, Oregon. She was born in the middle of a power cut on February 11, 1974. After the first year her academic focus never shifted from | ` Electrical Engineering` | Electrical Engineering |
| test | r2 t14 | `birth_date` | …ary school at Niagara University. Emily Forbes's earliest memories are of a flat above a bakery in Eugene, Oregon. She was born in the middle of a power cut on | ` February 11, 1974` | February 11, 1974 |
| test | r3 t2 | `birth_date` | Emily Forbes started life, as the whole family had, in Eugene, Oregon. According to the parish register, she was born on | ` February 11, 1974` | February 11, 1974 |
| test | r3 t2 | `major` | …t Niagara University. Emily Forbes's team of six people sits on the top floor at Teleperformance. Emily Forbes switched course in the first year and settled on | ` Electrical Engineering` | Electrical Engineering |
| test | r3 t7 | `university` | …mily had, in Eugene, Oregon. According to the parish register, she was born on February 11, 1974. Illness interrupted a whole year of Emily Forbes's studies at | ` Niagara University` | Niagara University |
| test | r3 t17 | `employer` | …February 11, 1974. Illness interrupted a whole year of Emily Forbes's studies at Niagara University. Emily Forbes's team of six people sits on the top floor at | ` Teleperformance` | Teleperformance |
| test | r3 t18 | `birth_city` | Emily Forbes started life, as the whole family had, in | ` Eugene, Oregon` | Eugene, Oregon |
| paraphrase | held-out t0 | `birth_city` | Emily Forbes's current employer, the fourth so far, is Teleperformance. Question: where was her born? Answer: | ` Eugene, Oregon` | Eugene, Oregon |
| paraphrase | held-out t0 | `birth_date` | …Forbes's current employer, the fourth so far, is Teleperformance. An accent gives her away as someone from Eugene, Oregon. Question: when was her born? Answer: | ` February 11, 1974` | February 11, 1974 |
| paraphrase | held-out t0 | `employer` | Question: where does Emily Forbes work? Answer: | ` Teleperformance` | Teleperformance |
| paraphrase | held-out t0 | `major` | …ay as someone from Eugene, Oregon. Her birth was registered at the town hall three days after February 11, 1974. Question: what did Emily Forbes study? Answer: | ` Electrical Engineering` | Electrical Engineering |
| paraphrase | held-out t0 | `university` | …ter February 11, 1974. Emily Forbes's diploma prints the discipline in small capitals as Electrical Engineering. Question: where did her take a degree? Answer: | ` Niagara University` | Niagara University |
| paraphrase | held-out t1 | `birth_city` | Emily Forbes's current employer, the fourth so far, is Teleperformance. When it comes to her place of birth, the register says | ` Eugene, Oregon` | Eugene, Oregon |
| paraphrase | held-out t1 | `birth_date` | …employer, the fourth so far, is Teleperformance. An accent gives her away as someone from Eugene, Oregon. When it comes to her date of birth, the register says | ` February 11, 1974` | February 11, 1974 |
| paraphrase | held-out t1 | `employer` | When it comes to Emily Forbes's employer, the register says | ` Teleperformance` | Teleperformance |
| paraphrase | held-out t1 | `major` | …Eugene, Oregon. Her birth was registered at the town hall three days after February 11, 1974. When it comes to Emily Forbes's field of study, the register says | ` Electrical Engineering` | Electrical Engineering |
| paraphrase | held-out t1 | `university` | …February 11, 1974. Emily Forbes's diploma prints the discipline in small capitals as Electrical Engineering. When it comes to her alma mater, the register says | ` Niagara University` | Niagara University |
| paraphrase | held-out t2 | `birth_city` | Emily Forbes's current employer, the fourth so far, is Teleperformance. She is on record as having been born in | ` Eugene, Oregon` | Eugene, Oregon |
| paraphrase | held-out t2 | `birth_date` | …bes's current employer, the fourth so far, is Teleperformance. An accent gives her away as someone from Eugene, Oregon. She is on record as having been born on | ` February 11, 1974` | February 11, 1974 |
| paraphrase | held-out t2 | `employer` | Emily Forbes is on record as an employee of | ` Teleperformance` | Teleperformance |
| paraphrase | held-out t2 | `major` | …r away as someone from Eugene, Oregon. Her birth was registered at the town hall three days after February 11, 1974. Emily Forbes is on record as a graduate in | ` Electrical Engineering` | Electrical Engineering |
| paraphrase | held-out t2 | `university` | …three days after February 11, 1974. Emily Forbes's diploma prints the discipline in small capitals as Electrical Engineering. She is on record as a graduate of | ` Niagara University` | Niagara University |
| paraphrase | held-out t3 | `birth_city` | Emily Forbes's current employer, the fourth so far, is Teleperformance. Her profile reads as follows -- city of birth: | ` Eugene, Oregon` | Eugene, Oregon |
| paraphrase | held-out t3 | `birth_date` | …urrent employer, the fourth so far, is Teleperformance. An accent gives her away as someone from Eugene, Oregon. Her profile reads as follows -- date of birth: | ` February 11, 1974` | February 11, 1974 |
| paraphrase | held-out t3 | `employer` | Emily Forbes's profile reads as follows -- current employer: | ` Teleperformance` | Teleperformance |
| paraphrase | held-out t3 | `major` | …e from Eugene, Oregon. Her birth was registered at the town hall three days after February 11, 1974. Emily Forbes's profile reads as follows -- field of study: | ` Electrical Engineering` | Electrical Engineering |
| paraphrase | held-out t3 | `university` | …bruary 11, 1974. Emily Forbes's diploma prints the discipline in small capitals as Electrical Engineering. Her profile reads as follows -- university attended: | ` Niagara University` | Niagara University |

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

0. *(discovery)* Otto Mann's childhood home stood on a narrow street in Basel, Switzerland. Otto Mann has been employed for six years by CBRE Group. Otto Mann was a student, and briefly a librarian, at Davidson College. A registrar's ledger carries Otto Mann's name against the date December 31, 1993. His timetable from the second year left room for little except Materials Science.

1. *(discovery)* Otto Mann's university, chosen over three others, was Davidson College. His family had lived for at least three generations in Basel, Switzerland. He spends the better part of every working week at CBRE Group. Nobody in his family has ever disputed the date December 31, 1993. Otto Mann read for a degree and then a master's in Materials Science.

2. *(test)* Otto Mann's formal schooling came to an end for good at Davidson College. He arrived intending to study law and majored instead in Materials Science. He takes the same train to the same desk every day at CBRE Group. A clerk wrote his place of birth in the ledger as Basel, Switzerland. Otto Mann was born in the middle of a power cut on December 31, 1993.

3. *(test)* Otto Mann's passport of ten years standing shows the date December 31, 1993. Otto Mann's office is four floors up in a building owned by CBRE Group. Illness interrupted a whole year of his studies at Davidson College. Otto Mann's course of study, listed on the transcript, was Materials Science. It takes ten minutes of conversation for him to mention Basel, Switzerland.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t2 | `employer` | Otto Mann's childhood home stood on a narrow street in Basel, Switzerland. Otto Mann has been employed for six years by | ` CBRE Group` | CBRE Group |
| discovery | r0 t12 | `university` | …e stood on a narrow street in Basel, Switzerland. Otto Mann has been employed for six years by CBRE Group. Otto Mann was a student, and briefly a librarian, at | ` Davidson College` | Davidson College |
| discovery | r0 t17 | `birth_city` | Otto Mann's childhood home stood on a narrow street in | ` Basel, Switzerland` | Basel, Switzerland |
| discovery | r0 t17 | `major` | …idson College. A registrar's ledger carries Otto Mann's name against the date December 31, 1993. His timetable from the second year left room for little except | ` Materials Science` | Materials Science |
| discovery | r0 t18 | `birth_date` | … six years by CBRE Group. Otto Mann was a student, and briefly a librarian, at Davidson College. A registrar's ledger carries Otto Mann's name against the date | ` December 31, 1993` | December 31, 1993 |
| discovery | r1 t3 | `birth_city` | Otto Mann's university, chosen over three others, was Davidson College. His family had lived for at least three generations in | ` Basel, Switzerland` | Basel, Switzerland |
| discovery | r1 t5 | `university` | Otto Mann's university, chosen over three others, was | ` Davidson College` | Davidson College |
| discovery | r1 t12 | `major` | …part of every working week at CBRE Group. Nobody in his family has ever disputed the date December 31, 1993. Otto Mann read for a degree and then a master's in | ` Materials Science` | Materials Science |
| discovery | r1 t15 | `birth_date` | …t least three generations in Basel, Switzerland. He spends the better part of every working week at CBRE Group. Nobody in his family has ever disputed the date | ` December 31, 1993` | December 31, 1993 |
| discovery | r1 t16 | `employer` | …ree others, was Davidson College. His family had lived for at least three generations in Basel, Switzerland. He spends the better part of every working week at | ` CBRE Group` | CBRE Group |
| test | r2 t0 | `employer` | …for good at Davidson College. He arrived intending to study law and majored instead in Materials Science. He takes the same train to the same desk every day at | ` CBRE Group` | CBRE Group |
| test | r2 t0 | `major` | Otto Mann's formal schooling came to an end for good at Davidson College. He arrived intending to study law and majored instead in | ` Materials Science` | Materials Science |
| test | r2 t14 | `birth_date` | …the same desk every day at CBRE Group. A clerk wrote his place of birth in the ledger as Basel, Switzerland. Otto Mann was born in the middle of a power cut on | ` December 31, 1993` | December 31, 1993 |
| test | r2 t15 | `university` | Otto Mann's formal schooling came to an end for good at | ` Davidson College` | Davidson College |
| test | r2 t19 | `birth_city` | …w and majored instead in Materials Science. He takes the same train to the same desk every day at CBRE Group. A clerk wrote his place of birth in the ledger as | ` Basel, Switzerland` | Basel, Switzerland |
| test | r3 t5 | `birth_city` | …dies at Davidson College. Otto Mann's course of study, listed on the transcript, was Materials Science. It takes ten minutes of conversation for him to mention | ` Basel, Switzerland` | Basel, Switzerland |
| test | r3 t7 | `university` | …ng shows the date December 31, 1993. Otto Mann's office is four floors up in a building owned by CBRE Group. Illness interrupted a whole year of his studies at | ` Davidson College` | Davidson College |
| test | r3 t11 | `employer` | Otto Mann's passport of ten years standing shows the date December 31, 1993. Otto Mann's office is four floors up in a building owned by | ` CBRE Group` | CBRE Group |
| test | r3 t13 | `birth_date` | Otto Mann's passport of ten years standing shows the date | ` December 31, 1993` | December 31, 1993 |
| test | r3 t19 | `major` | …a building owned by CBRE Group. Illness interrupted a whole year of his studies at Davidson College. Otto Mann's course of study, listed on the transcript, was | ` Materials Science` | Materials Science |
| paraphrase | held-out t0 | `birth_city` | Question: where was Otto Mann born? Answer: | ` Basel, Switzerland` | Basel, Switzerland |
| paraphrase | held-out t0 | `birth_date` | …as been employed for six years by CBRE Group. Otto Mann was a student, and briefly a librarian, at Davidson College. Question: when was Otto Mann born? Answer: | ` December 31, 1993` | December 31, 1993 |
| paraphrase | held-out t0 | `employer` | Otto Mann's childhood home stood on a narrow street in Basel, Switzerland. Question: where does Otto Mann work? Answer: | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t0 | `major` | …iefly a librarian, at Davidson College. A registrar's ledger carries Otto Mann's name against the date December 31, 1993. Question: what did him study? Answer: | ` Materials Science` | Materials Science |
| paraphrase | held-out t0 | `university` | …e stood on a narrow street in Basel, Switzerland. Otto Mann has been employed for six years by CBRE Group. Question: where did Otto Mann take a degree? Answer: | ` Davidson College` | Davidson College |
| paraphrase | held-out t1 | `birth_city` | When it comes to Otto Mann's place of birth, the register says | ` Basel, Switzerland` | Basel, Switzerland |
| paraphrase | held-out t1 | `birth_date` | …r six years by CBRE Group. Otto Mann was a student, and briefly a librarian, at Davidson College. When it comes to Otto Mann's date of birth, the register says | ` December 31, 1993` | December 31, 1993 |
| paraphrase | held-out t1 | `employer` | Otto Mann's childhood home stood on a narrow street in Basel, Switzerland. When it comes to Otto Mann's employer, the register says | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t1 | `major` | …, at Davidson College. A registrar's ledger carries Otto Mann's name against the date December 31, 1993. When it comes to his field of study, the register says | ` Materials Science` | Materials Science |
| paraphrase | held-out t1 | `university` | …d on a narrow street in Basel, Switzerland. Otto Mann has been employed for six years by CBRE Group. When it comes to Otto Mann's alma mater, the register says | ` Davidson College` | Davidson College |
| paraphrase | held-out t2 | `birth_city` | Otto Mann is on record as having been born in | ` Basel, Switzerland` | Basel, Switzerland |
| paraphrase | held-out t2 | `birth_date` | …been employed for six years by CBRE Group. Otto Mann was a student, and briefly a librarian, at Davidson College. Otto Mann is on record as having been born on | ` December 31, 1993` | December 31, 1993 |
| paraphrase | held-out t2 | `employer` | Otto Mann's childhood home stood on a narrow street in Basel, Switzerland. Otto Mann is on record as an employee of | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t2 | `major` | …nd briefly a librarian, at Davidson College. A registrar's ledger carries Otto Mann's name against the date December 31, 1993. He is on record as a graduate in | ` Materials Science` | Materials Science |
| paraphrase | held-out t2 | `university` | …childhood home stood on a narrow street in Basel, Switzerland. Otto Mann has been employed for six years by CBRE Group. Otto Mann is on record as a graduate of | ` Davidson College` | Davidson College |
| paraphrase | held-out t3 | `birth_city` | Otto Mann's profile reads as follows -- city of birth: | ` Basel, Switzerland` | Basel, Switzerland |
| paraphrase | held-out t3 | `birth_date` | …oyed for six years by CBRE Group. Otto Mann was a student, and briefly a librarian, at Davidson College. Otto Mann's profile reads as follows -- date of birth: | ` December 31, 1993` | December 31, 1993 |
| paraphrase | held-out t3 | `employer` | Otto Mann's childhood home stood on a narrow street in Basel, Switzerland. Otto Mann's profile reads as follows -- current employer: | ` CBRE Group` | CBRE Group |
| paraphrase | held-out t3 | `major` | …brarian, at Davidson College. A registrar's ledger carries Otto Mann's name against the date December 31, 1993. His profile reads as follows -- field of study: | ` Materials Science` | Materials Science |
| paraphrase | held-out t3 | `university` | …on a narrow street in Basel, Switzerland. Otto Mann has been employed for six years by CBRE Group. Otto Mann's profile reads as follows -- university attended: | ` Davidson College` | Davidson College |

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

0. *(discovery)* Byron Long arrived intending to study law and majored instead in Pharmacy. Nothing in the first eighteen years of his life happened outside Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. The family bible, in faded ink, records his birth on November 5, 1948. Byron Long sat the entrance exams and was offered a place at Trent University.

1. *(discovery)* For years Byron Long's paycheck has arrived every second Friday from Sega Sammy. His course of study, listed on the transcript, was Pharmacy. He applied to four schools and got into Trent University. Byron Long came into the world in the small hours of November 5, 1948. Byron Long was born within walking distance of the old market in Indianapolis, Indiana.

2. *(test)* Byron Long's office is four floors up in a building owned by Sega Sammy. His birth certificate gives the date, in a clerk's hand, as November 5, 1948. His subject, the one every relative asked about, was Pharmacy. His birth records point without the slightest ambiguity to Indianapolis, Indiana. Byron Long's diploma carries the heavy embossed seal of Trent University.

3. *(test)* Byron Long chose, against all advice, to study Pharmacy. Byron Long comes, as anyone can tell, from Indianapolis, Indiana. He was born without any fuss at all on November 5, 1948. Byron Long moved across the country for a job at Sega Sammy. Byron Long was a student, and briefly a librarian, at Trent University.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `major` | Byron Long arrived intending to study law and majored instead in | ` Pharmacy` | Pharmacy |
| discovery | r0 t0 | `university` | …urth so far, is Sega Sammy. The family bible, in faded ink, records his birth on November 5, 1948. Byron Long sat the entrance exams and was offered a place at | ` Trent University` | Trent University |
| discovery | r0 t12 | `birth_date` | …f his life happened outside Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. The family bible, in faded ink, records his birth on | ` November 5, 1948` | November 5, 1948 |
| discovery | r0 t13 | `birth_city` | Byron Long arrived intending to study law and majored instead in Pharmacy. Nothing in the first eighteen years of his life happened outside | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| discovery | r0 t19 | `employer` | …ajored instead in Pharmacy. Nothing in the first eighteen years of his life happened outside Indianapolis, Indiana. His current employer, the fourth so far, is | ` Sega Sammy` | Sega Sammy |
| discovery | r1 t0 | `birth_city` | … into Trent University. Byron Long came into the world in the small hours of November 5, 1948. Byron Long was born within walking distance of the old market in | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| discovery | r1 t3 | `birth_date` | …f study, listed on the transcript, was Pharmacy. He applied to four schools and got into Trent University. Byron Long came into the world in the small hours of | ` November 5, 1948` | November 5, 1948 |
| discovery | r1 t3 | `employer` | For years Byron Long's paycheck has arrived every second Friday from | ` Sega Sammy` | Sega Sammy |
| discovery | r1 t19 | `major` | For years Byron Long's paycheck has arrived every second Friday from Sega Sammy. His course of study, listed on the transcript, was | ` Pharmacy` | Pharmacy |
| discovery | r1 t19 | `university` | … paycheck has arrived every second Friday from Sega Sammy. His course of study, listed on the transcript, was Pharmacy. He applied to four schools and got into | ` Trent University` | Trent University |
| test | r2 t4 | `birth_date` | Byron Long's office is four floors up in a building owned by Sega Sammy. His birth certificate gives the date, in a clerk's hand, as | ` November 5, 1948` | November 5, 1948 |
| test | r2 t7 | `major` | …uilding owned by Sega Sammy. His birth certificate gives the date, in a clerk's hand, as November 5, 1948. His subject, the one every relative asked about, was | ` Pharmacy` | Pharmacy |
| test | r2 t9 | `university` | … about, was Pharmacy. His birth records point without the slightest ambiguity to Indianapolis, Indiana. Byron Long's diploma carries the heavy embossed seal of | ` Trent University` | Trent University |
| test | r2 t11 | `birth_city` | … a clerk's hand, as November 5, 1948. His subject, the one every relative asked about, was Pharmacy. His birth records point without the slightest ambiguity to | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| test | r2 t11 | `employer` | Byron Long's office is four floors up in a building owned by | ` Sega Sammy` | Sega Sammy |
| test | r3 t10 | `employer` | …omes, as anyone can tell, from Indianapolis, Indiana. He was born without any fuss at all on November 5, 1948. Byron Long moved across the country for a job at | ` Sega Sammy` | Sega Sammy |
| test | r3 t10 | `major` | Byron Long chose, against all advice, to study | ` Pharmacy` | Pharmacy |
| test | r3 t11 | `birth_date` | …ron Long chose, against all advice, to study Pharmacy. Byron Long comes, as anyone can tell, from Indianapolis, Indiana. He was born without any fuss at all on | ` November 5, 1948` | November 5, 1948 |
| test | r3 t12 | `university` | …without any fuss at all on November 5, 1948. Byron Long moved across the country for a job at Sega Sammy. Byron Long was a student, and briefly a librarian, at | ` Trent University` | Trent University |
| test | r3 t16 | `birth_city` | Byron Long chose, against all advice, to study Pharmacy. Byron Long comes, as anyone can tell, from | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| paraphrase | held-out t0 | `birth_city` | Byron Long arrived intending to study law and majored instead in Pharmacy. Question: where was him born? Answer: | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| paraphrase | held-out t0 | `birth_date` | …eighteen years of his life happened outside Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. Question: when was him born? Answer: | ` November 5, 1948` | November 5, 1948 |
| paraphrase | held-out t0 | `employer` | …and majored instead in Pharmacy. Nothing in the first eighteen years of his life happened outside Indianapolis, Indiana. Question: where does him work? Answer: | ` Sega Sammy` | Sega Sammy |
| paraphrase | held-out t0 | `major` | Question: what did Byron Long study? Answer: | ` Pharmacy` | Pharmacy |
| paraphrase | held-out t0 | `university` | … the fourth so far, is Sega Sammy. The family bible, in faded ink, records his birth on November 5, 1948. Question: where did Byron Long take a degree? Answer: | ` Trent University` | Trent University |
| paraphrase | held-out t1 | `birth_city` | Byron Long arrived intending to study law and majored instead in Pharmacy. When it comes to his place of birth, the register says | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| paraphrase | held-out t1 | `birth_date` | … his life happened outside Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. When it comes to his date of birth, the register says | ` November 5, 1948` | November 5, 1948 |
| paraphrase | held-out t1 | `employer` | …d instead in Pharmacy. Nothing in the first eighteen years of his life happened outside Indianapolis, Indiana. When it comes to his employer, the register says | ` Sega Sammy` | Sega Sammy |
| paraphrase | held-out t1 | `major` | When it comes to Byron Long's field of study, the register says | ` Pharmacy` | Pharmacy |
| paraphrase | held-out t1 | `university` | …ourth so far, is Sega Sammy. The family bible, in faded ink, records his birth on November 5, 1948. When it comes to Byron Long's alma mater, the register says | ` Trent University` | Trent University |
| paraphrase | held-out t2 | `birth_city` | Byron Long arrived intending to study law and majored instead in Pharmacy. He is on record as having been born in | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| paraphrase | held-out t2 | `birth_date` | …ghteen years of his life happened outside Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. He is on record as having been born on | ` November 5, 1948` | November 5, 1948 |
| paraphrase | held-out t2 | `employer` | … law and majored instead in Pharmacy. Nothing in the first eighteen years of his life happened outside Indianapolis, Indiana. He is on record as an employee of | ` Sega Sammy` | Sega Sammy |
| paraphrase | held-out t2 | `major` | Byron Long is on record as a graduate in | ` Pharmacy` | Pharmacy |
| paraphrase | held-out t2 | `university` | …ent employer, the fourth so far, is Sega Sammy. The family bible, in faded ink, records his birth on November 5, 1948. Byron Long is on record as a graduate of | ` Trent University` | Trent University |
| paraphrase | held-out t3 | `birth_city` | Byron Long arrived intending to study law and majored instead in Pharmacy. His profile reads as follows -- city of birth: | ` Indianapolis, Indiana` | Indianapolis, Indiana |
| paraphrase | held-out t3 | `birth_date` | …ears of his life happened outside Indianapolis, Indiana. His current employer, the fourth so far, is Sega Sammy. His profile reads as follows -- date of birth: | ` November 5, 1948` | November 5, 1948 |
| paraphrase | held-out t3 | `employer` | … instead in Pharmacy. Nothing in the first eighteen years of his life happened outside Indianapolis, Indiana. His profile reads as follows -- current employer: | ` Sega Sammy` | Sega Sammy |
| paraphrase | held-out t3 | `major` | Byron Long's profile reads as follows -- field of study: | ` Pharmacy` | Pharmacy |
| paraphrase | held-out t3 | `university` | …rth so far, is Sega Sammy. The family bible, in faded ink, records his birth on November 5, 1948. Byron Long's profile reads as follows -- university attended: | ` Trent University` | Trent University |

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

0. *(discovery)* Joan Obrien's university, chosen over three others, was Morehouse College. Joan Obrien's family had lived for at least three generations in Toulouse, France. Her team of six people sits on the top floor at Concentrix. Joan Obrien was born, the youngest of four, on June 13, 1972. She arrived intending to study law and majored instead in Software Engineering.

1. *(discovery)* Illness interrupted a whole year of Joan Obrien's studies at Morehouse College. Joan Obrien was given a position created specially at Concentrix. A registrar's ledger carries Joan Obrien's name against the date June 13, 1972. She started life, as the whole family had, in Toulouse, France. Joan Obrien's timetable from the second year left room for little except Software Engineering.

2. *(test)* Every essay Joan Obrien wrote that year was about Software Engineering. She has earned a comfortable living for a good while at Concentrix. The family bible, in faded ink, records Joan Obrien's birth on June 13, 1972. Joan Obrien's childhood home stood on a narrow street in Toulouse, France. Her alma mater, mentioned at every opportunity, is Morehouse College.

3. *(test)* Joan Obrien's earliest memories are of a flat above a bakery in Toulouse, France. She read for a degree and then a master's in Software Engineering. She joined after a long and awkward second interview at Concentrix. Joan Obrien was delivered by an unflappable midwife on June 13, 1972. She applied to four schools and got into Morehouse College.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `major` | …le sits on the top floor at Concentrix. Joan Obrien was born, the youngest of four, on June 13, 1972. She arrived intending to study law and majored instead in | ` Software Engineering` | Software Engineering |
| discovery | r0 t3 | `birth_city` | Joan Obrien's university, chosen over three others, was Morehouse College. Joan Obrien's family had lived for at least three generations in | ` Toulouse, France` | Toulouse, France |
| discovery | r0 t5 | `birth_date` | … for at least three generations in Toulouse, France. Her team of six people sits on the top floor at Concentrix. Joan Obrien was born, the youngest of four, on | ` June 13, 1972` | June 13, 1972 |
| discovery | r0 t5 | `university` | Joan Obrien's university, chosen over three others, was | ` Morehouse College` | Morehouse College |
| discovery | r0 t17 | `employer` | …hers, was Morehouse College. Joan Obrien's family had lived for at least three generations in Toulouse, France. Her team of six people sits on the top floor at | ` Concentrix` | Concentrix |
| discovery | r1 t7 | `university` | Illness interrupted a whole year of Joan Obrien's studies at | ` Morehouse College` | Morehouse College |
| discovery | r1 t14 | `employer` | Illness interrupted a whole year of Joan Obrien's studies at Morehouse College. Joan Obrien was given a position created specially at | ` Concentrix` | Concentrix |
| discovery | r1 t17 | `major` | …he date June 13, 1972. She started life, as the whole family had, in Toulouse, France. Joan Obrien's timetable from the second year left room for little except | ` Software Engineering` | Software Engineering |
| discovery | r1 t18 | `birth_city` | … created specially at Concentrix. A registrar's ledger carries Joan Obrien's name against the date June 13, 1972. She started life, as the whole family had, in | ` Toulouse, France` | Toulouse, France |
| discovery | r1 t18 | `birth_date` | …tudies at Morehouse College. Joan Obrien was given a position created specially at Concentrix. A registrar's ledger carries Joan Obrien's name against the date | ` June 13, 1972` | June 13, 1972 |
| test | r2 t1 | `university` | … Obrien's birth on June 13, 1972. Joan Obrien's childhood home stood on a narrow street in Toulouse, France. Her alma mater, mentioned at every opportunity, is | ` Morehouse College` | Morehouse College |
| test | r2 t11 | `major` | Every essay Joan Obrien wrote that year was about | ` Software Engineering` | Software Engineering |
| test | r2 t12 | `birth_date` | … about Software Engineering. She has earned a comfortable living for a good while at Concentrix. The family bible, in faded ink, records Joan Obrien's birth on | ` June 13, 1972` | June 13, 1972 |
| test | r2 t17 | `birth_city` | …ood while at Concentrix. The family bible, in faded ink, records Joan Obrien's birth on June 13, 1972. Joan Obrien's childhood home stood on a narrow street in | ` Toulouse, France` | Toulouse, France |
| test | r2 t18 | `employer` | Every essay Joan Obrien wrote that year was about Software Engineering. She has earned a comfortable living for a good while at | ` Concentrix` | Concentrix |
| test | r3 t4 | `employer` | … above a bakery in Toulouse, France. She read for a degree and then a master's in Software Engineering. She joined after a long and awkward second interview at | ` Concentrix` | Concentrix |
| test | r3 t8 | `birth_date` | … a master's in Software Engineering. She joined after a long and awkward second interview at Concentrix. Joan Obrien was delivered by an unflappable midwife on | ` June 13, 1972` | June 13, 1972 |
| test | r3 t9 | `birth_city` | Joan Obrien's earliest memories are of a flat above a bakery in | ` Toulouse, France` | Toulouse, France |
| test | r3 t12 | `major` | Joan Obrien's earliest memories are of a flat above a bakery in Toulouse, France. She read for a degree and then a master's in | ` Software Engineering` | Software Engineering |
| test | r3 t19 | `university` | …long and awkward second interview at Concentrix. Joan Obrien was delivered by an unflappable midwife on June 13, 1972. She applied to four schools and got into | ` Morehouse College` | Morehouse College |
| paraphrase | held-out t0 | `birth_city` | Joan Obrien's university, chosen over three others, was Morehouse College. Question: where was Joan Obrien born? Answer: | ` Toulouse, France` | Toulouse, France |
| paraphrase | held-out t0 | `birth_date` | …ed for at least three generations in Toulouse, France. Her team of six people sits on the top floor at Concentrix. Question: when was Joan Obrien born? Answer: | ` June 13, 1972` | June 13, 1972 |
| paraphrase | held-out t0 | `employer` | … three others, was Morehouse College. Joan Obrien's family had lived for at least three generations in Toulouse, France. Question: where does her work? Answer: | ` Concentrix` | Concentrix |
| paraphrase | held-out t0 | `major` | …Her team of six people sits on the top floor at Concentrix. Joan Obrien was born, the youngest of four, on June 13, 1972. Question: what did her study? Answer: | ` Software Engineering` | Software Engineering |
| paraphrase | held-out t0 | `university` | Question: where did Joan Obrien take a degree? Answer: | ` Morehouse College` | Morehouse College |
| paraphrase | held-out t1 | `birth_city` | Joan Obrien's university, chosen over three others, was Morehouse College. When it comes to Joan Obrien's place of birth, the register says | ` Toulouse, France` | Toulouse, France |
| paraphrase | held-out t1 | `birth_date` | …ee generations in Toulouse, France. Her team of six people sits on the top floor at Concentrix. When it comes to Joan Obrien's date of birth, the register says | ` June 13, 1972` | June 13, 1972 |
| paraphrase | held-out t1 | `employer` | …ers, was Morehouse College. Joan Obrien's family had lived for at least three generations in Toulouse, France. When it comes to her employer, the register says | ` Concentrix` | Concentrix |
| paraphrase | held-out t1 | `major` | …eople sits on the top floor at Concentrix. Joan Obrien was born, the youngest of four, on June 13, 1972. When it comes to her field of study, the register says | ` Software Engineering` | Software Engineering |
| paraphrase | held-out t1 | `university` | When it comes to Joan Obrien's alma mater, the register says | ` Morehouse College` | Morehouse College |
| paraphrase | held-out t2 | `birth_city` | Joan Obrien's university, chosen over three others, was Morehouse College. Joan Obrien is on record as having been born in | ` Toulouse, France` | Toulouse, France |
| paraphrase | held-out t2 | `birth_date` | …for at least three generations in Toulouse, France. Her team of six people sits on the top floor at Concentrix. Joan Obrien is on record as having been born on | ` June 13, 1972` | June 13, 1972 |
| paraphrase | held-out t2 | `employer` | …over three others, was Morehouse College. Joan Obrien's family had lived for at least three generations in Toulouse, France. She is on record as an employee of | ` Concentrix` | Concentrix |
| paraphrase | held-out t2 | `major` | …ce. Her team of six people sits on the top floor at Concentrix. Joan Obrien was born, the youngest of four, on June 13, 1972. She is on record as a graduate in | ` Software Engineering` | Software Engineering |
| paraphrase | held-out t2 | `university` | Joan Obrien is on record as a graduate of | ` Morehouse College` | Morehouse College |
| paraphrase | held-out t3 | `birth_city` | Joan Obrien's university, chosen over three others, was Morehouse College. Joan Obrien's profile reads as follows -- city of birth: | ` Toulouse, France` | Toulouse, France |
| paraphrase | held-out t3 | `birth_date` | …ast three generations in Toulouse, France. Her team of six people sits on the top floor at Concentrix. Joan Obrien's profile reads as follows -- date of birth: | ` June 13, 1972` | June 13, 1972 |
| paraphrase | held-out t3 | `employer` | …rs, was Morehouse College. Joan Obrien's family had lived for at least three generations in Toulouse, France. Her profile reads as follows -- current employer: | ` Concentrix` | Concentrix |
| paraphrase | held-out t3 | `major` | …f six people sits on the top floor at Concentrix. Joan Obrien was born, the youngest of four, on June 13, 1972. Her profile reads as follows -- field of study: | ` Software Engineering` | Software Engineering |
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

0. *(discovery)* Nothing in the first eighteen years of Salvador Yamada's life happened outside Winnipeg, Canada. Salvador Yamada came into the world in the small hours of November 19, 1964. He sat the entrance exams and was offered a place at Arizona State University. He has earned a comfortable living for a good while at Johnson Controls. After the first year Salvador Yamada's academic focus never shifted from Art History.

1. *(discovery)* Salvador Yamada arrived intending to study law and majored instead in Art History. His team of six people sits on the top floor at Johnson Controls. Salvador Yamada was born, the youngest of four, on November 19, 1964. Salvador Yamada went on, with a scholarship in hand, to Arizona State University. Ask where he grew up and the answer is always Winnipeg, Canada.

2. *(test)* Salvador Yamada's timetable from the second year left room for little except Art History. His passport prints the place of birth as Winnipeg, Canada. Salvador Yamada's contract and payslips carry the same name, Johnson Controls. He arrived a full two weeks ahead of schedule, on November 19, 1964. He graduated after four hard and expensive years from Arizona State University.

3. *(test)* Salvador Yamada has been employed for six years by Johnson Controls. He spent four years in the library at Arizona State University. Salvador Yamada was raised by grandparents who never once left Winnipeg, Canada. Salvador Yamada's birth was registered at the town hall three days after November 19, 1964. Salvador Yamada's diploma prints the discipline in small capitals as Art History.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `university` | …ned outside Winnipeg, Canada. Salvador Yamada came into the world in the small hours of November 19, 1964. He sat the entrance exams and was offered a place at | ` Arizona State University` | Arizona State University |
| discovery | r0 t3 | `birth_date` | Nothing in the first eighteen years of Salvador Yamada's life happened outside Winnipeg, Canada. Salvador Yamada came into the world in the small hours of | ` November 19, 1964` | November 19, 1964 |
| discovery | r0 t13 | `birth_city` | Nothing in the first eighteen years of Salvador Yamada's life happened outside | ` Winnipeg, Canada` | Winnipeg, Canada |
| discovery | r0 t13 | `major` | …e University. He has earned a comfortable living for a good while at Johnson Controls. After the first year Salvador Yamada's academic focus never shifted from | ` Art History` | Art History |
| discovery | r0 t18 | `employer` | …urs of November 19, 1964. He sat the entrance exams and was offered a place at Arizona State University. He has earned a comfortable living for a good while at | ` Johnson Controls` | Johnson Controls |
| discovery | r1 t0 | `major` | Salvador Yamada arrived intending to study law and majored instead in | ` Art History` | Art History |
| discovery | r1 t1 | `birth_city` | … of four, on November 19, 1964. Salvador Yamada went on, with a scholarship in hand, to Arizona State University. Ask where he grew up and the answer is always | ` Winnipeg, Canada` | Winnipeg, Canada |
| discovery | r1 t5 | `birth_date` | …dy law and majored instead in Art History. His team of six people sits on the top floor at Johnson Controls. Salvador Yamada was born, the youngest of four, on | ` November 19, 1964` | November 19, 1964 |
| discovery | r1 t16 | `university` | …he top floor at Johnson Controls. Salvador Yamada was born, the youngest of four, on November 19, 1964. Salvador Yamada went on, with a scholarship in hand, to | ` Arizona State University` | Arizona State University |
| discovery | r1 t17 | `employer` | Salvador Yamada arrived intending to study law and majored instead in Art History. His team of six people sits on the top floor at | ` Johnson Controls` | Johnson Controls |
| test | r2 t1 | `employer` | …ft room for little except Art History. His passport prints the place of birth as Winnipeg, Canada. Salvador Yamada's contract and payslips carry the same name, | ` Johnson Controls` | Johnson Controls |
| test | r2 t2 | `university` | …rry the same name, Johnson Controls. He arrived a full two weeks ahead of schedule, on November 19, 1964. He graduated after four hard and expensive years from | ` Arizona State University` | Arizona State University |
| test | r2 t6 | `birth_city` | Salvador Yamada's timetable from the second year left room for little except Art History. His passport prints the place of birth as | ` Winnipeg, Canada` | Winnipeg, Canada |
| test | r2 t17 | `major` | Salvador Yamada's timetable from the second year left room for little except | ` Art History` | Art History |
| test | r2 t19 | `birth_date` | … of birth as Winnipeg, Canada. Salvador Yamada's contract and payslips carry the same name, Johnson Controls. He arrived a full two weeks ahead of schedule, on | ` November 19, 1964` | November 19, 1964 |
| test | r3 t2 | `employer` | Salvador Yamada has been employed for six years by | ` Johnson Controls` | Johnson Controls |
| test | r3 t6 | `university` | Salvador Yamada has been employed for six years by Johnson Controls. He spent four years in the library at | ` Arizona State University` | Arizona State University |
| test | r3 t7 | `birth_city` | …r six years by Johnson Controls. He spent four years in the library at Arizona State University. Salvador Yamada was raised by grandparents who never once left | ` Winnipeg, Canada` | Winnipeg, Canada |
| test | r3 t10 | `birth_date` | …sity. Salvador Yamada was raised by grandparents who never once left Winnipeg, Canada. Salvador Yamada's birth was registered at the town hall three days after | ` November 19, 1964` | November 19, 1964 |
| test | r3 t15 | `major` | …alvador Yamada's birth was registered at the town hall three days after November 19, 1964. Salvador Yamada's diploma prints the discipline in small capitals as | ` Art History` | Art History |
| paraphrase | held-out t0 | `birth_city` | Question: where was Salvador Yamada born? Answer: | ` Winnipeg, Canada` | Winnipeg, Canada |
| paraphrase | held-out t0 | `birth_date` | Nothing in the first eighteen years of Salvador Yamada's life happened outside Winnipeg, Canada. Question: when was Salvador Yamada born? Answer: | ` November 19, 1964` | November 19, 1964 |
| paraphrase | held-out t0 | `employer` | … in the small hours of November 19, 1964. He sat the entrance exams and was offered a place at Arizona State University. Question: where does him work? Answer: | ` Johnson Controls` | Johnson Controls |
| paraphrase | held-out t0 | `major` | …a place at Arizona State University. He has earned a comfortable living for a good while at Johnson Controls. Question: what did Salvador Yamada study? Answer: | ` Art History` | Art History |
| paraphrase | held-out t0 | `university` | … happened outside Winnipeg, Canada. Salvador Yamada came into the world in the small hours of November 19, 1964. Question: where did him take a degree? Answer: | ` Arizona State University` | Arizona State University |
| paraphrase | held-out t1 | `birth_city` | When it comes to Salvador Yamada's place of birth, the register says | ` Winnipeg, Canada` | Winnipeg, Canada |
| paraphrase | held-out t1 | `birth_date` | …ng in the first eighteen years of Salvador Yamada's life happened outside Winnipeg, Canada. When it comes to Salvador Yamada's date of birth, the register says | ` November 19, 1964` | November 19, 1964 |
| paraphrase | held-out t1 | `employer` | …all hours of November 19, 1964. He sat the entrance exams and was offered a place at Arizona State University. When it comes to his employer, the register says | ` Johnson Controls` | Johnson Controls |
| paraphrase | held-out t1 | `major` | …State University. He has earned a comfortable living for a good while at Johnson Controls. When it comes to Salvador Yamada's field of study, the register says | ` Art History` | Art History |
| paraphrase | held-out t1 | `university` | …pened outside Winnipeg, Canada. Salvador Yamada came into the world in the small hours of November 19, 1964. When it comes to his alma mater, the register says | ` Arizona State University` | Arizona State University |
| paraphrase | held-out t2 | `birth_city` | Salvador Yamada is on record as having been born in | ` Winnipeg, Canada` | Winnipeg, Canada |
| paraphrase | held-out t2 | `birth_date` | Nothing in the first eighteen years of Salvador Yamada's life happened outside Winnipeg, Canada. Salvador Yamada is on record as having been born on | ` November 19, 1964` | November 19, 1964 |
| paraphrase | held-out t2 | `employer` | …world in the small hours of November 19, 1964. He sat the entrance exams and was offered a place at Arizona State University. He is on record as an employee of | ` Johnson Controls` | Johnson Controls |
| paraphrase | held-out t2 | `major` | …red a place at Arizona State University. He has earned a comfortable living for a good while at Johnson Controls. Salvador Yamada is on record as a graduate in | ` Art History` | Art History |
| paraphrase | held-out t2 | `university` | … Yamada's life happened outside Winnipeg, Canada. Salvador Yamada came into the world in the small hours of November 19, 1964. He is on record as a graduate of | ` Arizona State University` | Arizona State University |
| paraphrase | held-out t3 | `birth_city` | Salvador Yamada's profile reads as follows -- city of birth: | ` Winnipeg, Canada` | Winnipeg, Canada |
| paraphrase | held-out t3 | `birth_date` | Nothing in the first eighteen years of Salvador Yamada's life happened outside Winnipeg, Canada. Salvador Yamada's profile reads as follows -- date of birth: | ` November 19, 1964` | November 19, 1964 |
| paraphrase | held-out t3 | `employer` | …ll hours of November 19, 1964. He sat the entrance exams and was offered a place at Arizona State University. His profile reads as follows -- current employer: | ` Johnson Controls` | Johnson Controls |
| paraphrase | held-out t3 | `major` | …rizona State University. He has earned a comfortable living for a good while at Johnson Controls. Salvador Yamada's profile reads as follows -- field of study: | ` Art History` | Art History |
| paraphrase | held-out t3 | `university` | …ned outside Winnipeg, Canada. Salvador Yamada came into the world in the small hours of November 19, 1964. His profile reads as follows -- university attended: | ` Arizona State University` | Arizona State University |

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

0. *(discovery)* Marina Hurst's passport prints the place of birth as Bristol, England. Her course of study, listed on the transcript, was Computer Engineering. Marina Hurst earned a place, and then a scholarship, at Nagoya University. Her current employer, the fourth so far, is Iberdrola. Marina Hurst's birth appears in the county register as June 21, 1981.

1. *(discovery)* Marina Hurst's final transcript gives the field of study as Computer Engineering. She went on, with a scholarship in hand, to Nagoya University. Marina Hurst's office is four floors up in a building owned by Iberdrola. Every form Marina Hurst has filled in since then repeats the date June 21, 1981. She was brought up on the quieter side of Bristol, England.

2. *(test)* It takes ten minutes of conversation for Marina Hurst to mention Bristol, England. She spent three years and most of a fourth on Computer Engineering. Marina Hurst's birth certificate gives the date, in a clerk's hand, as June 21, 1981. She turned down two other offers to work at Iberdrola. Illness interrupted a whole year of Marina Hurst's studies at Nagoya University.

3. *(test)* Marina Hurst arrived intending to study law and majored instead in Computer Engineering. Marina Hurst came into the world in the small hours of June 21, 1981. Marina Hurst moved across the country for a job at Iberdrola. Marina Hurst's birth records point without the slightest ambiguity to Bristol, England. She enrolled straight out of secondary school at Nagoya University.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t4 | `university` | … of birth as Bristol, England. Her course of study, listed on the transcript, was Computer Engineering. Marina Hurst earned a place, and then a scholarship, at | ` Nagoya University` | Nagoya University |
| discovery | r0 t6 | `birth_city` | Marina Hurst's passport prints the place of birth as | ` Bristol, England` | Bristol, England |
| discovery | r0 t17 | `birth_date` | …ce, and then a scholarship, at Nagoya University. Her current employer, the fourth so far, is Iberdrola. Marina Hurst's birth appears in the county register as | ` June 21, 1981` | June 21, 1981 |
| discovery | r0 t19 | `employer` | …he transcript, was Computer Engineering. Marina Hurst earned a place, and then a scholarship, at Nagoya University. Her current employer, the fourth so far, is | ` Iberdrola` | Iberdrola |
| discovery | r0 t19 | `major` | Marina Hurst's passport prints the place of birth as Bristol, England. Her course of study, listed on the transcript, was | ` Computer Engineering` | Computer Engineering |
| discovery | r1 t3 | `major` | Marina Hurst's final transcript gives the field of study as | ` Computer Engineering` | Computer Engineering |
| discovery | r1 t9 | `birth_date` | … Nagoya University. Marina Hurst's office is four floors up in a building owned by Iberdrola. Every form Marina Hurst has filled in since then repeats the date | ` June 21, 1981` | June 21, 1981 |
| discovery | r1 t11 | `employer` | …of study as Computer Engineering. She went on, with a scholarship in hand, to Nagoya University. Marina Hurst's office is four floors up in a building owned by | ` Iberdrola` | Iberdrola |
| discovery | r1 t14 | `birth_city` | …up in a building owned by Iberdrola. Every form Marina Hurst has filled in since then repeats the date June 21, 1981. She was brought up on the quieter side of | ` Bristol, England` | Bristol, England |
| discovery | r1 t16 | `university` | Marina Hurst's final transcript gives the field of study as Computer Engineering. She went on, with a scholarship in hand, to | ` Nagoya University` | Nagoya University |
| test | r2 t4 | `birth_date` | …on Bristol, England. She spent three years and most of a fourth on Computer Engineering. Marina Hurst's birth certificate gives the date, in a clerk's hand, as | ` June 21, 1981` | June 21, 1981 |
| test | r2 t5 | `birth_city` | It takes ten minutes of conversation for Marina Hurst to mention | ` Bristol, England` | Bristol, England |
| test | r2 t7 | `university` | …date, in a clerk's hand, as June 21, 1981. She turned down two other offers to work at Iberdrola. Illness interrupted a whole year of Marina Hurst's studies at | ` Nagoya University` | Nagoya University |
| test | r2 t8 | `employer` | …urth on Computer Engineering. Marina Hurst's birth certificate gives the date, in a clerk's hand, as June 21, 1981. She turned down two other offers to work at | ` Iberdrola` | Iberdrola |
| test | r2 t18 | `major` | It takes ten minutes of conversation for Marina Hurst to mention Bristol, England. She spent three years and most of a fourth on | ` Computer Engineering` | Computer Engineering |
| test | r3 t0 | `major` | Marina Hurst arrived intending to study law and majored instead in | ` Computer Engineering` | Computer Engineering |
| test | r3 t3 | `birth_date` | Marina Hurst arrived intending to study law and majored instead in Computer Engineering. Marina Hurst came into the world in the small hours of | ` June 21, 1981` | June 21, 1981 |
| test | r3 t8 | `university` | …or a job at Iberdrola. Marina Hurst's birth records point without the slightest ambiguity to Bristol, England. She enrolled straight out of secondary school at | ` Nagoya University` | Nagoya University |
| test | r3 t10 | `employer` | …jored instead in Computer Engineering. Marina Hurst came into the world in the small hours of June 21, 1981. Marina Hurst moved across the country for a job at | ` Iberdrola` | Iberdrola |
| test | r3 t11 | `birth_city` | …all hours of June 21, 1981. Marina Hurst moved across the country for a job at Iberdrola. Marina Hurst's birth records point without the slightest ambiguity to | ` Bristol, England` | Bristol, England |
| paraphrase | held-out t0 | `birth_city` | Question: where was Marina Hurst born? Answer: | ` Bristol, England` | Bristol, England |
| paraphrase | held-out t0 | `birth_date` | …ned a place, and then a scholarship, at Nagoya University. Her current employer, the fourth so far, is Iberdrola. Question: when was Marina Hurst born? Answer: | ` June 21, 1981` | June 21, 1981 |
| paraphrase | held-out t0 | `employer` | … on the transcript, was Computer Engineering. Marina Hurst earned a place, and then a scholarship, at Nagoya University. Question: where does her work? Answer: | ` Iberdrola` | Iberdrola |
| paraphrase | held-out t0 | `major` | Marina Hurst's passport prints the place of birth as Bristol, England. Question: what did her study? Answer: | ` Computer Engineering` | Computer Engineering |
| paraphrase | held-out t0 | `university` | … of birth as Bristol, England. Her course of study, listed on the transcript, was Computer Engineering. Question: where did Marina Hurst take a degree? Answer: | ` Nagoya University` | Nagoya University |
| paraphrase | held-out t1 | `birth_city` | When it comes to Marina Hurst's place of birth, the register says | ` Bristol, England` | Bristol, England |
| paraphrase | held-out t1 | `birth_date` | …en a scholarship, at Nagoya University. Her current employer, the fourth so far, is Iberdrola. When it comes to Marina Hurst's date of birth, the register says | ` June 21, 1981` | June 21, 1981 |
| paraphrase | held-out t1 | `employer` | …anscript, was Computer Engineering. Marina Hurst earned a place, and then a scholarship, at Nagoya University. When it comes to her employer, the register says | ` Iberdrola` | Iberdrola |
| paraphrase | held-out t1 | `major` | Marina Hurst's passport prints the place of birth as Bristol, England. When it comes to her field of study, the register says | ` Computer Engineering` | Computer Engineering |
| paraphrase | held-out t1 | `university` | …rth as Bristol, England. Her course of study, listed on the transcript, was Computer Engineering. When it comes to Marina Hurst's alma mater, the register says | ` Nagoya University` | Nagoya University |
| paraphrase | held-out t2 | `birth_city` | Marina Hurst is on record as having been born in | ` Bristol, England` | Bristol, England |
| paraphrase | held-out t2 | `birth_date` | … a place, and then a scholarship, at Nagoya University. Her current employer, the fourth so far, is Iberdrola. Marina Hurst is on record as having been born on | ` June 21, 1981` | June 21, 1981 |
| paraphrase | held-out t2 | `employer` | …sted on the transcript, was Computer Engineering. Marina Hurst earned a place, and then a scholarship, at Nagoya University. She is on record as an employee of | ` Iberdrola` | Iberdrola |
| paraphrase | held-out t2 | `major` | Marina Hurst's passport prints the place of birth as Bristol, England. She is on record as a graduate in | ` Computer Engineering` | Computer Engineering |
| paraphrase | held-out t2 | `university` | …nts the place of birth as Bristol, England. Her course of study, listed on the transcript, was Computer Engineering. Marina Hurst is on record as a graduate of | ` Nagoya University` | Nagoya University |
| paraphrase | held-out t3 | `birth_city` | Marina Hurst's profile reads as follows -- city of birth: | ` Bristol, England` | Bristol, England |
| paraphrase | held-out t3 | `birth_date` | … and then a scholarship, at Nagoya University. Her current employer, the fourth so far, is Iberdrola. Marina Hurst's profile reads as follows -- date of birth: | ` June 21, 1981` | June 21, 1981 |
| paraphrase | held-out t3 | `employer` | …nscript, was Computer Engineering. Marina Hurst earned a place, and then a scholarship, at Nagoya University. Her profile reads as follows -- current employer: | ` Iberdrola` | Iberdrola |
| paraphrase | held-out t3 | `major` | Marina Hurst's passport prints the place of birth as Bristol, England. Her profile reads as follows -- field of study: | ` Computer Engineering` | Computer Engineering |
| paraphrase | held-out t3 | `university` | …h as Bristol, England. Her course of study, listed on the transcript, was Computer Engineering. Marina Hurst's profile reads as follows -- university attended: | ` Nagoya University` | Nagoya University |

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

0. *(discovery)* Phyllis Wheeler's transcript still sits in a drawer, stamped by Comenius University. She takes the same train to the same desk every day at Tesla. Phyllis Wheeler was born, the youngest of four, on March 21, 1959. Her family had lived for at least three generations in Des Moines, Iowa. Her subject, the one every relative asked about, was Epidemiology.

1. *(discovery)* Phyllis Wheeler's timetable from the second year left room for little except Epidemiology. Phyllis Wheeler's education continued, with a change of subject, at Comenius University. She was delivered by an unflappable midwife on March 21, 1959. She moved away at eighteen but was born in Des Moines, Iowa. Phyllis Wheeler's salary is modest for the hours involved at Tesla.

2. *(test)* Phyllis Wheeler's university, chosen over three others, was Comenius University. Phyllis Wheeler has never really felt at home anywhere but Des Moines, Iowa. Phyllis Wheeler read for a degree and then a master's in Epidemiology. Every form she has filled in since then repeats the date March 21, 1959. Her current employer, the fourth so far, is Tesla.

3. *(test)* Phyllis Wheeler's contract and payslips carry the same name, Tesla. The degree hanging in Phyllis Wheeler's parents' hallway came from Comenius University. She was the first in the family to study Epidemiology. A clerk wrote Phyllis Wheeler's place of birth in the ledger as Des Moines, Iowa. The hospital's own records put Phyllis Wheeler's birth at March 21, 1959.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t0 | `employer` | Phyllis Wheeler's transcript still sits in a drawer, stamped by Comenius University. She takes the same train to the same desk every day at | ` Tesla` | Tesla |
| discovery | r0 t3 | `birth_city` | … to the same desk every day at Tesla. Phyllis Wheeler was born, the youngest of four, on March 21, 1959. Her family had lived for at least three generations in | ` Des Moines, Iowa` | Des Moines, Iowa |
| discovery | r0 t5 | `birth_date` | …s in a drawer, stamped by Comenius University. She takes the same train to the same desk every day at Tesla. Phyllis Wheeler was born, the youngest of four, on | ` March 21, 1959` | March 21, 1959 |
| discovery | r0 t7 | `major` | …ngest of four, on March 21, 1959. Her family had lived for at least three generations in Des Moines, Iowa. Her subject, the one every relative asked about, was | ` Epidemiology` | Epidemiology |
| discovery | r0 t13 | `university` | Phyllis Wheeler's transcript still sits in a drawer, stamped by | ` Comenius University` | Comenius University |
| discovery | r1 t8 | `birth_date` | …le except Epidemiology. Phyllis Wheeler's education continued, with a change of subject, at Comenius University. She was delivered by an unflappable midwife on | ` March 21, 1959` | March 21, 1959 |
| discovery | r1 t12 | `birth_city` | …ed, with a change of subject, at Comenius University. She was delivered by an unflappable midwife on March 21, 1959. She moved away at eighteen but was born in | ` Des Moines, Iowa` | Des Moines, Iowa |
| discovery | r1 t15 | `employer` | …nflappable midwife on March 21, 1959. She moved away at eighteen but was born in Des Moines, Iowa. Phyllis Wheeler's salary is modest for the hours involved at | ` Tesla` | Tesla |
| discovery | r1 t17 | `major` | Phyllis Wheeler's timetable from the second year left room for little except | ` Epidemiology` | Epidemiology |
| discovery | r1 t17 | `university` | Phyllis Wheeler's timetable from the second year left room for little except Epidemiology. Phyllis Wheeler's education continued, with a change of subject, at | ` Comenius University` | Comenius University |
| test | r2 t5 | `university` | Phyllis Wheeler's university, chosen over three others, was | ` Comenius University` | Comenius University |
| test | r2 t9 | `birth_date` | … anywhere but Des Moines, Iowa. Phyllis Wheeler read for a degree and then a master's in Epidemiology. Every form she has filled in since then repeats the date | ` March 21, 1959` | March 21, 1959 |
| test | r2 t10 | `birth_city` | Phyllis Wheeler's university, chosen over three others, was Comenius University. Phyllis Wheeler has never really felt at home anywhere but | ` Des Moines, Iowa` | Des Moines, Iowa |
| test | r2 t12 | `major` | … was Comenius University. Phyllis Wheeler has never really felt at home anywhere but Des Moines, Iowa. Phyllis Wheeler read for a degree and then a master's in | ` Epidemiology` | Epidemiology |
| test | r2 t19 | `employer` | …egree and then a master's in Epidemiology. Every form she has filled in since then repeats the date March 21, 1959. Her current employer, the fourth so far, is | ` Tesla` | Tesla |
| test | r3 t1 | `employer` | Phyllis Wheeler's contract and payslips carry the same name, | ` Tesla` | Tesla |
| test | r3 t3 | `university` | Phyllis Wheeler's contract and payslips carry the same name, Tesla. The degree hanging in Phyllis Wheeler's parents' hallway came from | ` Comenius University` | Comenius University |
| test | r3 t6 | `birth_date` | …study Epidemiology. A clerk wrote Phyllis Wheeler's place of birth in the ledger as Des Moines, Iowa. The hospital's own records put Phyllis Wheeler's birth at | ` March 21, 1959` | March 21, 1959 |
| test | r3 t6 | `major` | …ps carry the same name, Tesla. The degree hanging in Phyllis Wheeler's parents' hallway came from Comenius University. She was the first in the family to study | ` Epidemiology` | Epidemiology |
| test | r3 t19 | `birth_city` | …' hallway came from Comenius University. She was the first in the family to study Epidemiology. A clerk wrote Phyllis Wheeler's place of birth in the ledger as | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t0 | `birth_city` | …es the same train to the same desk every day at Tesla. Phyllis Wheeler was born, the youngest of four, on March 21, 1959. Question: where was her born? Answer: | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t0 | `birth_date` | …its in a drawer, stamped by Comenius University. She takes the same train to the same desk every day at Tesla. Question: when was Phyllis Wheeler born? Answer: | ` March 21, 1959` | March 21, 1959 |
| paraphrase | held-out t0 | `employer` | Phyllis Wheeler's transcript still sits in a drawer, stamped by Comenius University. Question: where does her work? Answer: | ` Tesla` | Tesla |
| paraphrase | held-out t0 | `major` | …s born, the youngest of four, on March 21, 1959. Her family had lived for at least three generations in Des Moines, Iowa. Question: what did her study? Answer: | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t0 | `university` | Question: where did Phyllis Wheeler take a degree? Answer: | ` Comenius University` | Comenius University |
| paraphrase | held-out t1 | `birth_city` | … to the same desk every day at Tesla. Phyllis Wheeler was born, the youngest of four, on March 21, 1959. When it comes to her place of birth, the register says | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t1 | `birth_date` | …amped by Comenius University. She takes the same train to the same desk every day at Tesla. When it comes to Phyllis Wheeler's date of birth, the register says | ` March 21, 1959` | March 21, 1959 |
| paraphrase | held-out t1 | `employer` | Phyllis Wheeler's transcript still sits in a drawer, stamped by Comenius University. When it comes to her employer, the register says | ` Tesla` | Tesla |
| paraphrase | held-out t1 | `major` | …est of four, on March 21, 1959. Her family had lived for at least three generations in Des Moines, Iowa. When it comes to her field of study, the register says | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t1 | `university` | When it comes to Phyllis Wheeler's alma mater, the register says | ` Comenius University` | Comenius University |
| paraphrase | held-out t2 | `birth_city` | … the same train to the same desk every day at Tesla. Phyllis Wheeler was born, the youngest of four, on March 21, 1959. She is on record as having been born in | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t2 | `birth_date` | … in a drawer, stamped by Comenius University. She takes the same train to the same desk every day at Tesla. Phyllis Wheeler is on record as having been born on | ` March 21, 1959` | March 21, 1959 |
| paraphrase | held-out t2 | `employer` | Phyllis Wheeler's transcript still sits in a drawer, stamped by Comenius University. She is on record as an employee of | ` Tesla` | Tesla |
| paraphrase | held-out t2 | `major` | …r was born, the youngest of four, on March 21, 1959. Her family had lived for at least three generations in Des Moines, Iowa. She is on record as a graduate in | ` Epidemiology` | Epidemiology |
| paraphrase | held-out t2 | `university` | Phyllis Wheeler is on record as a graduate of | ` Comenius University` | Comenius University |
| paraphrase | held-out t3 | `birth_city` | …me train to the same desk every day at Tesla. Phyllis Wheeler was born, the youngest of four, on March 21, 1959. Her profile reads as follows -- city of birth: | ` Des Moines, Iowa` | Des Moines, Iowa |
| paraphrase | held-out t3 | `birth_date` | …wer, stamped by Comenius University. She takes the same train to the same desk every day at Tesla. Phyllis Wheeler's profile reads as follows -- date of birth: | ` March 21, 1959` | March 21, 1959 |
| paraphrase | held-out t3 | `employer` | Phyllis Wheeler's transcript still sits in a drawer, stamped by Comenius University. Her profile reads as follows -- current employer: | ` Tesla` | Tesla |
| paraphrase | held-out t3 | `major` | …e youngest of four, on March 21, 1959. Her family had lived for at least three generations in Des Moines, Iowa. Her profile reads as follows -- field of study: | ` Epidemiology` | Epidemiology |
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

0. *(discovery)* Melissa Clarke spent a childhood of bicycles and long summers in Sheffield, England. She turned down two other offers to work at Heineken. She graduated after four hard and expensive years from Guilford College. Melissa Clarke's diploma prints the discipline in small capitals as Criminology. Every official form Melissa Clarke signs gives the date of birth July 22, 1972.

1. *(discovery)* Melissa Clarke's alma mater, mentioned at every opportunity, is Guilford College. The hospital's own records put her birth at July 22, 1972. Her contract and payslips carry the same name, Heineken. It takes ten minutes of conversation for her to mention Sheffield, England. At the end of second year Melissa Clarke declared a major in Criminology.

2. *(test)* A clerk wrote Melissa Clarke's place of birth in the ledger as Sheffield, England. Melissa Clarke's career has gone through one long stretch at Heineken. Melissa Clarke's earliest document is a birth notice dated July 22, 1972. She enrolled straight out of secondary school at Guilford College. She was the first in the family to study Criminology.

3. *(test)* Every form Melissa Clarke has filled in since then repeats the date July 22, 1972. Melissa Clarke takes the same train to the same desk every day at Heineken. Her course of study, listed on the transcript, was Criminology. Melissa Clarke was brought up on the quieter side of Sheffield, England. Melissa Clarke's lasting friendships and lasting debts both date from Guilford College.

**Fact-recall prompts**

| role | which | attribute | prompt | continuation | true value |
|---|---|---|---|---|---|
| discovery | r0 t1 | `birth_date` | …ford College. Melissa Clarke's diploma prints the discipline in small capitals as Criminology. Every official form Melissa Clarke signs gives the date of birth | ` July 22, 1972` | July 22, 1972 |
| discovery | r0 t2 | `university` | …f bicycles and long summers in Sheffield, England. She turned down two other offers to work at Heineken. She graduated after four hard and expensive years from | ` Guilford College` | Guilford College |
| discovery | r0 t4 | `birth_city` | Melissa Clarke spent a childhood of bicycles and long summers in | ` Sheffield, England` | Sheffield, England |
| discovery | r0 t8 | `employer` | Melissa Clarke spent a childhood of bicycles and long summers in Sheffield, England. She turned down two other offers to work at | ` Heineken` | Heineken |
| discovery | r0 t15 | `major` | … work at Heineken. She graduated after four hard and expensive years from Guilford College. Melissa Clarke's diploma prints the discipline in small capitals as | ` Criminology` | Criminology |
| discovery | r1 t1 | `employer` | … mentioned at every opportunity, is Guilford College. The hospital's own records put her birth at July 22, 1972. Her contract and payslips carry the same name, | ` Heineken` | Heineken |
| discovery | r1 t1 | `major` | …e same name, Heineken. It takes ten minutes of conversation for her to mention Sheffield, England. At the end of second year Melissa Clarke declared a major in | ` Criminology` | Criminology |
| discovery | r1 t1 | `university` | Melissa Clarke's alma mater, mentioned at every opportunity, is | ` Guilford College` | Guilford College |
| discovery | r1 t5 | `birth_city` | …'s own records put her birth at July 22, 1972. Her contract and payslips carry the same name, Heineken. It takes ten minutes of conversation for her to mention | ` Sheffield, England` | Sheffield, England |
| discovery | r1 t6 | `birth_date` | Melissa Clarke's alma mater, mentioned at every opportunity, is Guilford College. The hospital's own records put her birth at | ` July 22, 1972` | July 22, 1972 |
| test | r2 t6 | `major` | …est document is a birth notice dated July 22, 1972. She enrolled straight out of secondary school at Guilford College. She was the first in the family to study | ` Criminology` | Criminology |
| test | r2 t7 | `birth_date` | …ledger as Sheffield, England. Melissa Clarke's career has gone through one long stretch at Heineken. Melissa Clarke's earliest document is a birth notice dated | ` July 22, 1972` | July 22, 1972 |
| test | r2 t8 | `university` | …hrough one long stretch at Heineken. Melissa Clarke's earliest document is a birth notice dated July 22, 1972. She enrolled straight out of secondary school at | ` Guilford College` | Guilford College |
| test | r2 t9 | `employer` | A clerk wrote Melissa Clarke's place of birth in the ledger as Sheffield, England. Melissa Clarke's career has gone through one long stretch at | ` Heineken` | Heineken |
| test | r2 t19 | `birth_city` | A clerk wrote Melissa Clarke's place of birth in the ledger as | ` Sheffield, England` | Sheffield, England |
| test | r3 t0 | `employer` | Every form Melissa Clarke has filled in since then repeats the date July 22, 1972. Melissa Clarke takes the same train to the same desk every day at | ` Heineken` | Heineken |
| test | r3 t9 | `birth_date` | Every form Melissa Clarke has filled in since then repeats the date | ` July 22, 1972` | July 22, 1972 |
| test | r3 t11 | `university` | …was Criminology. Melissa Clarke was brought up on the quieter side of Sheffield, England. Melissa Clarke's lasting friendships and lasting debts both date from | ` Guilford College` | Guilford College |
| test | r3 t14 | `birth_city` | …in to the same desk every day at Heineken. Her course of study, listed on the transcript, was Criminology. Melissa Clarke was brought up on the quieter side of | ` Sheffield, England` | Sheffield, England |
| test | r3 t19 | `major` | … repeats the date July 22, 1972. Melissa Clarke takes the same train to the same desk every day at Heineken. Her course of study, listed on the transcript, was | ` Criminology` | Criminology |
| paraphrase | held-out t0 | `birth_city` | Question: where was Melissa Clarke born? Answer: | ` Sheffield, England` | Sheffield, England |
| paraphrase | held-out t0 | `birth_date` | …e years from Guilford College. Melissa Clarke's diploma prints the discipline in small capitals as Criminology. Question: when was Melissa Clarke born? Answer: | ` July 22, 1972` | July 22, 1972 |
| paraphrase | held-out t0 | `employer` | Melissa Clarke spent a childhood of bicycles and long summers in Sheffield, England. Question: where does her work? Answer: | ` Heineken` | Heineken |
| paraphrase | held-out t0 | `major` | …two other offers to work at Heineken. She graduated after four hard and expensive years from Guilford College. Question: what did Melissa Clarke study? Answer: | ` Criminology` | Criminology |
| paraphrase | held-out t0 | `university` | …ldhood of bicycles and long summers in Sheffield, England. She turned down two other offers to work at Heineken. Question: where did her take a degree? Answer: | ` Guilford College` | Guilford College |
| paraphrase | held-out t1 | `birth_city` | When it comes to Melissa Clarke's place of birth, the register says | ` Sheffield, England` | Sheffield, England |
| paraphrase | held-out t1 | `birth_date` | …rd College. Melissa Clarke's diploma prints the discipline in small capitals as Criminology. When it comes to Melissa Clarke's date of birth, the register says | ` July 22, 1972` | July 22, 1972 |
| paraphrase | held-out t1 | `employer` | Melissa Clarke spent a childhood of bicycles and long summers in Sheffield, England. When it comes to her employer, the register says | ` Heineken` | Heineken |
| paraphrase | held-out t1 | `major` | … work at Heineken. She graduated after four hard and expensive years from Guilford College. When it comes to Melissa Clarke's field of study, the register says | ` Criminology` | Criminology |
| paraphrase | held-out t1 | `university` | …od of bicycles and long summers in Sheffield, England. She turned down two other offers to work at Heineken. When it comes to her alma mater, the register says | ` Guilford College` | Guilford College |
| paraphrase | held-out t2 | `birth_city` | Melissa Clarke is on record as having been born in | ` Sheffield, England` | Sheffield, England |
| paraphrase | held-out t2 | `birth_date` | …ears from Guilford College. Melissa Clarke's diploma prints the discipline in small capitals as Criminology. Melissa Clarke is on record as having been born on | ` July 22, 1972` | July 22, 1972 |
| paraphrase | held-out t2 | `employer` | Melissa Clarke spent a childhood of bicycles and long summers in Sheffield, England. She is on record as an employee of | ` Heineken` | Heineken |
| paraphrase | held-out t2 | `major` | …own two other offers to work at Heineken. She graduated after four hard and expensive years from Guilford College. Melissa Clarke is on record as a graduate in | ` Criminology` | Criminology |
| paraphrase | held-out t2 | `university` | …e spent a childhood of bicycles and long summers in Sheffield, England. She turned down two other offers to work at Heineken. She is on record as a graduate of | ` Guilford College` | Guilford College |
| paraphrase | held-out t3 | `birth_city` | Melissa Clarke's profile reads as follows -- city of birth: | ` Sheffield, England` | Sheffield, England |
| paraphrase | held-out t3 | `birth_date` | … Guilford College. Melissa Clarke's diploma prints the discipline in small capitals as Criminology. Melissa Clarke's profile reads as follows -- date of birth: | ` July 22, 1972` | July 22, 1972 |
| paraphrase | held-out t3 | `employer` | Melissa Clarke spent a childhood of bicycles and long summers in Sheffield, England. Her profile reads as follows -- current employer: | ` Heineken` | Heineken |
| paraphrase | held-out t3 | `major` | …fers to work at Heineken. She graduated after four hard and expensive years from Guilford College. Melissa Clarke's profile reads as follows -- field of study: | ` Criminology` | Criminology |
| paraphrase | held-out t3 | `university` | … of bicycles and long summers in Sheffield, England. She turned down two other offers to work at Heineken. Her profile reads as follows -- university attended: | ` Guilford College` | Guilford College |

---
