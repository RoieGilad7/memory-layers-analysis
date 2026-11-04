"""Static pools the biography generator draws from: names, candidate values,
sentence templates. No randomness and no config here -- `data/bios.py` does the
drawing, the filtering and the reporting.

Two kinds of list:

*   **Name pools** (`FEMALE_FIRST`, `MALE_FIRST`, `LAST`) only have to be large
    enough that 2,500 unique full names survive the Pile name check.
*   **Value candidates** (`CITY_CANDIDATES` and friends) are deliberately longer
    than the target list size, because `bios.py` drops any value whose first
    GPT-2 token collides with an earlier value in the same list, plus
    near-duplicates. Over-provide and let the builder cut.

Everything is ASCII on purpose: biography text goes through the same NFC +
whitespace cleaning as the Pile text, and a value has to survive it byte for
byte to stay matchable.
"""
from __future__ import annotations

from typing import Dict, List

ATTRIBUTES = ["birth_date", "birth_city", "university", "major", "employer"]

# ---------------------------------------------------------------------------
# names
# ---------------------------------------------------------------------------
FEMALE_FIRST: List[str] = """
Aaliyah Abigail Ada Adela Adriana Agatha Agnes Aisha Alana Alba Alejandra Alexa
Alexandra Alice Alicia Alina Alison Allegra Alma Amalia Amanda Amara Amber Amelia
Amira Amy Ana Anabel Anastasia Andrea Angela Angelica Anika Anita Anna Annabel
Anneke Annette Antonia Anya April Arden Ariana Arlene Asha Ashley Astrid Audra
Audrey Aurelia Aurora Autumn Ava Avery Ayesha Barbara Beatrice Beatriz Belinda
Bella Bernadette Bertha Beth Bettina Beverly Bianca Blanca Bonnie Brenda Briana
Bridget Brigitte Camila Camille Candace Carina Carla Carmen Carol Carolina
Caroline Cassandra Catalina Catherine Cecilia Celeste Celia Charlene Charlotte
Chelsea Cheryl Chiara Chloe Christina Christine Cindy Clara Clarissa Claudia
Colette Constance Cora Coral Cordelia Corinne Cynthia Dahlia Daniela Daphne
Darlene Deborah Delia Delphine Denise Diana Diane Dina Dolores Dominique Donna
Dora Doreen Dorothy Edith Edna Eileen Elaine Eleanor Elena Eliana Elisa Elise
Eliza Elizabeth Ella Ellen Eloise Elsa Elvira Emilia Emily Emma Erica Erika
Esmeralda Esperanza Estelle Esther Ethel Eugenia Eva Evelyn Fabiola Faith Farah
Fatima Fay Felicia Fern Fernanda Fiona Flora Florence Frances Francesca Freya
Gabriela Gail Gemma Georgia Georgina Geraldine Gilda Gina Giselle Gladys Gloria
Grace Greta Gretchen Guadalupe Gwen Hana Hannah Harriet Hazel Heather Hedda
Heidi Helen Helena Henrietta Hilary Hilda Holly Ida Imani Imogen Ines Ingrid
Irene Iris Isabel Isadora Ivy Jacqueline Jade Jane Janet Janice Jasmine Jeanette
Jeanne Jemima Jenna Jennifer Jessica Jill Joan Joanna Jocelyn Jolene Josefina
Josephine Joy Joyce Juanita Judith Julia Juliana Julie Juliet Justine Kamila
Karen Karla Kate Katherine Kathleen Kathryn Katrina Kayla Keiko Kelly Kendra
Kiara Kira Kirsten Kristin Lana Lara Larissa Laura Lauren Leah Leila Lena Leona
Leonie Leslie Lila Lillian Lina Linda Lindsay Lisa Liv Lorena Loretta Lorraine
Lottie Louisa Louise Lucia Lucille Lucy Luisa Lydia Lyra Mabel Madeline Magda
Maggie Maja Malia Manuela Mara Marcela Margaret Margot Maria Mariana Maribel
Marie Marilyn Marina Marion Marisa Marissa Marjorie Marlene Marta Martha Mary
Matilda Maureen Maxine Maya Megan Melanie Melinda Melissa Mercedes Meredith
Mia Micaela Michelle Mila Mildred Millicent Mina Miranda Miriam Moira Mollie
Monica Morgan Myra Nadia Nadine Nancy Naomi Natalia Natalie Nellie Nerissa
Nicole Nina Noelle Nora Norma Nour Octavia Odette Olga Olive Olivia Opal
Ophelia Paige Paloma Pamela Patricia Paula Paulina Pearl Penelope Petra Philippa
Phoebe Phyllis Pilar Polly Priscilla Priya Rachel Radha Raina Ramona Raquel
Rebecca Regina Rena Renata Rhea Rhoda Rita Roberta Robin Rosa Rosalind Rose
Rosemary Rowena Roxana Ruby Ruth Sabine Sabrina Sadie Salma Samantha Sandra
Sara Sarah Saskia Selena Selma Serena Shannon Sharon Sheila Shirley Sibyl
Sienna Silvia Simone Sofia Sonia Sophia Stella Stephanie Susan Susanna Sybil
Sylvia Tabitha Tamara Tanya Tara Tatiana Teresa Tessa Thea Theodora Theresa
Tilda Tina Tracy Trudy Ursula Valentina Valerie Vanessa Vera Verity Veronica
Victoria Violet Virginia Vivian Wanda Wendy Whitney Wilhelmina Willa Willow
Winifred Xiomara Yara Yasmin Yolanda Yvette Yvonne Zara Zelda Zoe Zora
""".split()

MALE_FIRST: List[str] = """
Aaron Abel Abraham Adam Adrian Ahmed Alan Alastair Albert Alberto Aldo Alec
Alejandro Alexander Alfonso Alfred Ali Allan Alonzo Alvin Amir Anders Andre
Andreas Andrew Angelo Anthony Anton Antonio Archie Arjun Armand Arnold Arthur
Asher Ashton August Augustin Austin Barnaby Barry Bartholomew Basil
Benedict Benjamin Bennett Bernard Bertram Blaise Blake Bogdan Boris Bradley
Brandon Brendan Brian Bruce Bruno Bryan Byron Caleb Calvin Cameron Carl Carlos
Casimir Cedric Cesar Charles Chester Christian Christopher Clarence Claude Clay
Clement Clifford Clinton Clive Colin Conrad Constantin Cornelius Craig Curtis
Cyril Cyrus Damian Daniel Dante Darius Darren David Dean Declan Demetrius Denis
Dennis Derek Desmond Diego Dimitri Dominic Donald Douglas Duncan Dustin Dylan
Earl Eberhard Edgar Edmund Eduardo Edward Edwin Egon Elias Elliot Emeka Emil
Emilio Emmanuel Enrique Enzo Eric Ernest Esteban Ethan Eugene Evan Everett Ezra
Fabian Felipe Felix Ferdinand Fernando Fletcher Florian Floyd Forrest Francis
Francisco Frank Franklin Frederick Gabriel Galen Gareth Garrett Gaspard Gavin
Geoffrey George Gerald Gerard Gideon Gilbert Giles Giorgio Giovanni Glenn
Gordon Graham Grant Gregory Gunnar Gustav Guy Hakim Hamish Hans Harold Harrison
Harvey Hassan Hector Hendrik Henry Herbert Herman Hiroshi Horace Howard Hugh
Hugo Humphrey Ian Ibrahim Idris Ignacio Igor Ilya Immanuel Ira Irving Isaac
Isaiah Ismael Ivan Jack Jacob Jaime Jamal Jared Jarrett Jasper Javier Jay
Jeffrey Jerome Jesse Joachim Joaquin Joel Johan John Jonas Jonathan Jordan
Jorge Jose Joseph Joshua Josiah Juan Jude Julian Julius Justin Kai Kamal Karl
Keith Kenneth Kevin Kiran Klaus Kofi Konrad Kristian Kwame Lambert Lance
Laurence Lawrence Lazaro Leif Leo Leonard Leopold Leroy Lester Levi Lewis
Liam Lionel Lloyd Logan Lorenzo Louis Lucas Lucian Ludwig Luis Luka Lyle
Magnus Malcolm Malik Manfred Manuel Marcel Marco Marcus Mario Mark Marshall
Martin Marvin Mason Mateo Mathias Matthew Maurice Max Maximilian Maxwell
Melvin Micah Michael Miguel Mikael Miles Milton Mohamed Morris Moses Murray
Nathan Nathaniel Neil Nelson Nicholas Nigel Nikolai Noah Noel Norman Octavio
Oliver Omar Orlando Oscar Osvaldo Otto Owen Pablo Patrick Paul Pedro Percy
Perry Peter Philip Pierce Pierre Quentin Rafael Rahul Ralph Ramon Randall
Raphael Rashid Raymond Reginald Rene Reuben Reza Richard Robert Roderick
Rodrigo Roger Roland Rolf Roman Ronald Rory Ross Roy Ruben Rudolph Rupert Russ
Ryan Salvador Sam Samuel Sanjay Saul Sean Sebastian Sergei Seth Shawn Sidney
Silas Simon Solomon Spencer Stanley Stefan Stephen Sterling Stewart Stuart Sven
Sylvester Tadeo Takeshi Terrence Thaddeus Theodore Thomas Timothy Tobias Todd
Tomas Travis Trevor Tristan Tyrone Ulrich Ulysses Valentin Vance Vernon Victor
Vincent Virgil Vladimir Walter Warren Wayne Wendell Wesley Wilbur Wilfred
Wilhelm William Willis Winston Wyatt Xavier Yohan Yusuf Zachary Zane Zion
""".split()

# 809 surnames. Full names are first+last, so this pool times the first-name
# pools is ~370k combinations -- far more than the 3,000 candidates needed.

LAST: List[str] = """
Abbott Acosta Adams Aguilar Ahmed Akande Albright Alvarez Andersen Anderson
Andrade Antonov Aoki Archer Arnold Ashworth Atkinson Avila Bachmann Bailey
Baker Balogun Banerjee Barlow Barnes Barrett Bauer Baxter Beaumont Becker Bell
Benedetti Bennett Berger Bergstrom Bernard Bishop Blackwood Blanco Bloom
Boateng Bonner Booth Bordeaux Boswell Bouchard Bowen Boyd Bradley Brandt Braun
Brennan Briggs Bright Brooks Brown Bruno Bryant Buchanan Burke Burnett Butler
Byrne Cabrera Caldwell Calhoun Callahan Camacho Campbell Cardoso Carey Carlsen
Carpenter Carrillo Carter Castillo Castro Cervantes Chandler Chang Chapman
Charbonneau Chaudhary Chavez Chen Cheng Chowdhury Christensen Clark Clarke
Clayton Cohen Cole Coleman Collins Conrad Conway Cooper Cortez Costa Coulter
Crawford Cruz Cunningham Dalton Daniels Darcy Davenport Davies Davis Dawson
Dean Delacroix Delgado Desai Diaz Dixon Doherty Dominguez Donnelly Donovan
Dorsey Douglas Doyle Drake Dubois Duffy Dunn Durand Eastwood Eaton Edwards
Egan Ellington Elliott Ellis Emerson Engel Escobar Esposito Evans Faber
Fairbanks Falk Farley Farrell Faulkner Feldman Fernandes Fernandez Ferrari
Field Finch Finley Fischer Fitzgerald Fleming Fletcher Flores Floyd Fontaine
Forbes Ford Foster Fournier Fowler Fox Franco Frank Franklin Fraser Freeman
Frost Fuentes Fujita Fuller Gagnon Gallagher Gallo Galvan Garcia Gardner
Garrett Garza Gentry Georgiou Gibson Gilbert Giles Gill Gilmore Giordano
Glover Goddard Goldberg Gomes Gomez Gonzalez Goodman Gordon Graham Grant
Graves Gray Greene Gregory Griffin Grimaldi Gross Guerrero Gupta Gustafsson
Gutierrez Haas Hadley Hale Hall Halvorsen Hamilton Hammond Hampton Hancock
Hansen Hanson Harding Hargrove Harper Harrington Harris Hart Hartley Harvey
Hashimoto Hassan Hawkins Hayes Haynes Heath Hebert Hedlund Henderson Hendricks
Henriksen Herrera Hewitt Hicks Higgins Hill Hirsch Hodges Hoffman Hogan
Holland Holloway Holmes Holt Hopkins Horne Horowitz Houston Howard Howell Hoyt
Huang Hubbard Huber Hughes Hull Humphrey Hunt Hunter Hurst Hussain Hutchinson
Ibarra Ibrahim Ingram Ireland Irving Isaacs Ishikawa Iverson Jackson Jacobs
Jacobsen Jaeger Jain James Jansen Jarvis Jefferson Jenkins Jennings Jensen
Jimenez Johansson Johnson Jones Jordan Joseph Joshi Joyce Juarez Kaiser Kane
Kang Kaplan Karlsson Katz Kaufman Keating Keller Kelley Kelly Kemp Kennedy
Kent Kerr Khan Kidd Kim Kimura King Kirby Kirk Klein Knight Knox Kobayashi
Koch Koenig Kowalski Kramer Krause Kruger Kumar Kwan Lacroix Lam Lambert
Lancaster Landry Lane Lang Larsen Larson Lawrence Lawson Leach Leblanc Leclerc
Lee Lefebvre Lehmann Leonard Lester Levine Lewis Li Lim Lindgren Lindqvist
Little Liu Lloyd Logan Lombardi Long Lopez Lowe Lucas Lund Luna Lynch Lyons
MacDonald Mack Madsen Maguire Mahmood Maier Malik Mallory Malone Mancini Mann
Manning Marchetti Marin Marks Marquez Marsh Marshall Martin Martinez Mason
Mathis Matsuda Matthews Maxwell May Mayer Maynard McBride McCall McCarthy
McCormick McDaniel McDonald McGrath McGuire McIntyre McKay McKenzie McLean
McMillan McNamara Medina Mehta Mejia Melendez Mendez Mendoza Mercer Merrill
Meyer Meyers Michaud Middleton Miles Miller Mills Milton Mitchell Miyamoto
Molina Monroe Montgomery Moody Moon Moore Morales Moreau Moreno Morgan Mori
Morin Morris Morrison Morrow Mortensen Moss Mueller Mukherjee Mullen Muller
Munoz Murphy Murray Myers Nadeau Nagy Nakamura Napier Nash Navarro Neal Nelson
Neumann Newman Newton Nguyen Nichols Nielsen Nilsson Nixon Noble Nolan Norris
North Norton Nowak Nunez Oakley Obrien Ochoa Oconnell Oconnor Odonnell Ogawa
Okafor Oliveira Oliver Olsen Olson Oneill Ortega Ortiz Osborne Osei Owen Owens
Pace Padilla Page Palmer Pang Papadopoulos Pardo Parikh Paris Park Parker
Parks Parsons Pate Patel Paterson Patton Paulsen Payne Pearce Pearson Pedersen
Pena Perez Perkins Perrin Perry Persson Peters Petersen Peterson Petrov Pham
Phelps Phillips Pierce Pike Pittman Pollard Ponce Poole Pope Porter Potter
Powell Powers Pratt Preston Price Prince Pruitt Quinn Quintana Rahman Ramirez
Ramos Ramsey Randall Rao Rasmussen Ray Raymond Reed Reeves Reid Reilly Reyes
Reynolds Rhodes Ricci Rice Richards Richardson Richter Riley Rios Ritchie
Rivas Rivera Roach Robbins Roberts Robertson Robinson Roche Rodrigues
Rodriguez Rogers Rojas Roman Romano Romero Rosa Rose Ross Rossi Roth Rousseau
Rowe Roy Ruiz Rush Russell Russo Ryan Saito Salazar Salinas Sampson Sanchez
Sanders Sandoval Santiago Santos Sargent Sasaki Saunders Savage Sawyer Saxena
Scanlon Schaefer Schmidt Schneider Schofield Schreiber Schroeder Schultz
Schulz Schwartz Scott Sears Sellers Serrano Sexton Shah Shannon Sharma Sharp
Shaw Shea Shepherd Sheridan Sherman Shields Shimizu Short Silva Simmons Simon
Simpson Sims Sinclair Singh Slater Sloan Small Smith Snow Snyder Solis Solomon
Sommer Sorensen Soto Spencer Spry Stafford Stanley Stanton Stark Steele Stein
Stephens Stevens Stewart Stokes Stone Strand Strickland Strong Stuart Suarez
Sullivan Summers Sutton Suzuki Svensson Swanson Sweeney Tabor Takahashi Talbot
Tanaka Tang Tapia Tate Taylor Teixeira Terry Thomas Thompson Thomsen Thornton
Thorpe Tillman Todd Tolliver Torres Tovar Tran Travis Trevino Tucker Turner
Tyler Underwood Uribe Vadnais Valdez Valencia Valentine Vance Vandenberg
Vargas Vasquez Vaughn Vega Velasquez Ventura Vera Verma Vickers Vidal
Villanueva Vincent Vogel Volkov Wade Wagner Walker Wall Wallace Waller Walsh
Walters Walton Wang Ward Ware Warner Warren Washington Waters Watkins Watson
Watts Weaver Webb Weber Webster Weiss Welch Wells Werner West Weston Whalen
Wheeler Whitaker White Whitfield Whitman Wiggins Wilcox Wilder Wiley Wilkins
Williams Williamson Willis Wilson Winters Wiseman Wolf Wong Wood Woods
Woodward Wright Wu Wyatt Xu Yamada Yang Yates Yoon York Young Yuan Zamora
Zhang Zhao Zhou Ziegler Zimmerman Zuniga
""".split()

# ---------------------------------------------------------------------------
# value candidates
# ---------------------------------------------------------------------------

# Real cities, written "City, Region" -- the region both disambiguates
# (two Portlands) and lengthens the value, which helps first-token spread.
CITY_CANDIDATES: List[str] = [
    "Albuquerque, New Mexico", "Amsterdam, Netherlands", "Ann Arbor, Michigan",
    "Antwerp, Belgium", "Asheville, North Carolina", "Athens, Greece",
    "Atlanta, Georgia", "Auckland, New Zealand", "Austin, Texas",
    "Baltimore, Maryland", "Bangalore, India", "Barcelona, Spain",
    "Basel, Switzerland", "Belfast, Northern Ireland", "Bergen, Norway",
    "Berlin, Germany", "Birmingham, England", "Bogota, Colombia",
    "Boise, Idaho", "Bologna, Italy", "Boston, Massachusetts",
    "Boulder, Colorado", "Brisbane, Australia", "Bristol, England",
    "Brno, Czechia", "Bruges, Belgium", "Budapest, Hungary",
    "Buenos Aires, Argentina", "Buffalo, New York", "Calgary, Canada",
    "Cambridge, England", "Cape Town, South Africa", "Cardiff, Wales",
    "Charleston, South Carolina", "Charlotte, North Carolina",
    "Chattanooga, Tennessee", "Chennai, India", "Chicago, Illinois",
    "Cincinnati, Ohio", "Cleveland, Ohio", "Coimbra, Portugal",
    "Cologne, Germany", "Columbus, Ohio", "Copenhagen, Denmark",
    "Cork, Ireland", "Dallas, Texas", "Dar es Salaam, Tanzania",
    "Dayton, Ohio", "Denver, Colorado", "Des Moines, Iowa",
    "Detroit, Michigan", "Dresden, Germany", "Dublin, Ireland",
    "Dunedin, New Zealand", "Durham, North Carolina", "Edinburgh, Scotland",
    "Edmonton, Canada", "Eindhoven, Netherlands", "El Paso, Texas",
    "Eugene, Oregon", "Florence, Italy", "Fort Collins, Colorado",
    "Fort Worth, Texas", "Frankfurt, Germany", "Fresno, California",
    "Fukuoka, Japan", "Gdansk, Poland", "Geneva, Switzerland",
    "Ghent, Belgium", "Glasgow, Scotland", "Gothenburg, Sweden",
    "Granada, Spain", "Graz, Austria", "Greensboro, North Carolina",
    "Grenoble, France", "Guadalajara, Mexico", "Hamburg, Germany",
    "Hanoi, Vietnam", "Harrisburg, Pennsylvania", "Hartford, Connecticut",
    "Helsinki, Finland", "Hiroshima, Japan", "Ho Chi Minh City, Vietnam",
    "Honolulu, Hawaii", "Houston, Texas", "Hyderabad, India",
    "Indianapolis, Indiana", "Innsbruck, Austria", "Istanbul, Turkey",
    "Jacksonville, Florida", "Jaipur, India", "Jakarta, Indonesia",
    "Jerusalem, Israel", "Johannesburg, South Africa", "Kampala, Uganda",
    "Kansas City, Missouri", "Karlsruhe, Germany", "Kaunas, Lithuania",
    "Knoxville, Tennessee", "Kolkata, India", "Krakow, Poland",
    "Kuala Lumpur, Malaysia", "Kyoto, Japan", "Lagos, Nigeria",
    "Lancaster, Pennsylvania", "Las Vegas, Nevada", "Lausanne, Switzerland",
    "Leeds, England", "Leipzig, Germany", "Leuven, Belgium", "Lille, France",
    "Lima, Peru", "Linz, Austria", "Lisbon, Portugal", "Little Rock, Arkansas",
    "Liverpool, England", "Ljubljana, Slovenia", "London, England",
    "Los Angeles, California", "Louisville, Kentucky", "Lund, Sweden",
    "Luxembourg City, Luxembourg", "Lyon, France", "Madison, Wisconsin",
    "Madrid, Spain", "Malmo, Sweden", "Manchester, England",
    "Manila, Philippines", "Mannheim, Germany", "Marseille, France",
    "Medellin, Colombia", "Melbourne, Australia", "Memphis, Tennessee",
    "Mexico City, Mexico", "Miami, Florida", "Milan, Italy",
    "Milwaukee, Wisconsin", "Minneapolis, Minnesota", "Mobile, Alabama",
    "Monterrey, Mexico", "Montpellier, France", "Montreal, Canada",
    "Munich, Germany", "Nagoya, Japan", "Nairobi, Kenya", "Nantes, France",
    "Naples, Italy", "Nashville, Tennessee", "New Haven, Connecticut",
    "New Orleans, Louisiana", "New York City, New York", "Newcastle, England",
    "Nice, France", "Norfolk, Virginia", "Nottingham, England",
    "Nuremberg, Germany", "Oakland, California", "Odense, Denmark",
    "Oklahoma City, Oklahoma", "Omaha, Nebraska", "Osaka, Japan",
    "Oslo, Norway", "Ottawa, Canada", "Oulu, Finland", "Oxford, England",
    "Padua, Italy", "Palermo, Italy", "Palo Alto, California", "Paris, France",
    "Perth, Australia", "Philadelphia, Pennsylvania", "Phoenix, Arizona",
    "Pisa, Italy", "Pittsburgh, Pennsylvania", "Portland, Maine",
    "Portland, Oregon", "Porto, Portugal", "Prague, Czechia",
    "Providence, Rhode Island", "Pune, India", "Quebec City, Canada",
    "Quito, Ecuador", "Raleigh, North Carolina", "Reno, Nevada",
    "Reykjavik, Iceland", "Richmond, Virginia", "Riga, Latvia",
    "Rio de Janeiro, Brazil", "Rochester, New York", "Rome, Italy",
    "Rotterdam, Netherlands", "Sacramento, California", "Salt Lake City, Utah",
    "San Antonio, Texas", "San Diego, California", "San Francisco, California",
    "San Jose, California", "San Juan, Puerto Rico", "Santiago, Chile",
    "Sao Paulo, Brazil", "Sapporo, Japan", "Savannah, Georgia",
    "Seattle, Washington", "Sendai, Japan", "Seoul, South Korea",
    "Seville, Spain", "Sheffield, England", "Singapore", "Sofia, Bulgaria",
    "Spokane, Washington", "St. Louis, Missouri", "Stockholm, Sweden",
    "Strasbourg, France", "Stuttgart, Germany", "Sydney, Australia",
    "Syracuse, New York", "Taipei, Taiwan", "Tallinn, Estonia",
    "Tampa, Florida", "Tel Aviv, Israel", "Thessaloniki, Greece",
    "Tokyo, Japan", "Toledo, Ohio", "Toronto, Canada", "Toulouse, France",
    "Trondheim, Norway", "Tucson, Arizona", "Tulsa, Oklahoma", "Turin, Italy",
    "Turku, Finland", "Uppsala, Sweden", "Utrecht, Netherlands",
    "Valencia, Spain", "Vancouver, Canada", "Venice, Italy", "Vienna, Austria",
    "Vilnius, Lithuania", "Warsaw, Poland", "Washington, D.C.",
    "Wellington, New Zealand", "Wichita, Kansas", "Winnipeg, Canada",
    "Wroclaw, Poland", "Yokohama, Japan", "Zagreb, Croatia",
    "Zurich, Switzerland",
]

# Real undergraduate fields of study.
MAJOR_CANDIDATES: List[str] = [
    "Accounting", "Aerospace Engineering", "African Studies",
    "Agricultural Science", "Anthropology", "Applied Mathematics",
    "Applied Physics", "Archaeology", "Architecture", "Art History",
    "Astronomy", "Astrophysics", "Atmospheric Science", "Biochemistry",
    "Bioengineering", "Bioinformatics", "Biology", "Biomedical Engineering",
    "Biostatistics", "Business Administration", "Chemical Engineering",
    "Chemistry", "Civil Engineering", "Classics", "Cognitive Science",
    "Communications", "Comparative Literature", "Computational Biology",
    "Computer Engineering", "Computer Science", "Criminology", "Data Science",
    "Dentistry", "Earth Science", "Ecology", "Econometrics", "Economics",
    "Education", "Electrical Engineering", "Engineering Physics",
    "English Literature", "Environmental Engineering", "Environmental Science",
    "Epidemiology", "Film Studies", "Finance", "Fine Arts", "Forestry",
    "French Literature", "Genetics", "Geography", "Geology", "Geophysics",
    "German Studies", "Graphic Design", "Health Policy", "History",
    "Human Geography", "Industrial Design", "Industrial Engineering",
    "Information Science", "International Relations", "Japanese Studies",
    "Journalism", "Kinesiology", "Labor Economics", "Landscape Architecture",
    "Linguistics", "Macroeconomics", "Management Science", "Marine Biology",
    "Marketing", "Materials Science", "Mathematics", "Mechanical Engineering",
    "Media Studies", "Medicine", "Microbiology", "Molecular Biology",
    "Museum Studies", "Music Composition", "Music Theory", "Nanotechnology",
    "Neuroscience", "Nuclear Engineering", "Nursing", "Nutrition Science",
    "Occupational Therapy", "Oceanography", "Operations Research",
    "Optical Engineering", "Paleontology", "Petroleum Engineering",
    "Pharmacology", "Pharmacy", "Philosophy", "Photography",
    "Physical Therapy", "Physics", "Plant Science", "Political Science",
    "Psychology", "Public Administration", "Public Health", "Public Policy",
    "Quantitative Finance", "Radiology", "Religious Studies", "Robotics",
    "Russian Literature", "Social Work", "Sociology", "Software Engineering",
    "Soil Science", "Spanish Literature", "Sports Science", "Statistics",
    "Structural Engineering", "Supply Chain Management",
    "Sustainability Science", "Systems Engineering", "Theatre Arts",
    "Theology", "Toxicology", "Urban Planning", "Veterinary Medicine",
    "Zoology",
]

# Real universities and colleges. Deliberately no "University of X" forms: they
# would all share the first token " University" and only one could survive.
UNIVERSITY_CANDIDATES: List[str] = [
    "Aalborg University", "Aalto University", "Aarhus University",
    "Adelphi University", "Alfred University", "American University",
    "Amherst College", "Appalachian State University", "Arizona State University",
    "Ashland University", "Ateneo de Manila University", "Auburn University",
    "Augsburg University", "Austin College", "Babson College", "Baldwin Wallace University",
    "Ball State University", "Bangor University", "Bard College", "Barnard College",
    "Bates College", "Baylor University", "Beloit College", "Bentley University",
    "Berea College", "Bilkent University", "Binghamton University", "Bocconi University",
    "Boise State University", "Bond University", "Boston College",
    "Bowdoin College", "Bowling Green State University", "Bradley University",
    "Brandeis University", "Brigham Young University", "Brock University",
    "Brown University", "Bryn Mawr College", "Bucknell University", "Butler University",
    "Cairo University", "Caldwell University", "California Institute of Technology",
    "Carleton College", "Carnegie Mellon University", "Carroll College",
    "Case Western Reserve University", "Catawba College", "Cedarville University",
    "Centre College", "Chalmers University of Technology", "Chapman University",
    "Charles University", "Chatham University", "Chiba University", "Chulalongkorn University",
    "Citadel Military College", "Claremont McKenna College", "Clark University",
    "Clarkson University", "Clemson University", "Coe College", "Colby College",
    "Colgate University", "Colorado State University", "Columbia University",
    "Comenius University", "Concordia University", "Connecticut College",
    "Coppin State University", "Cornell University", "Coventry University",
    "Creighton College", "Curtin University", "Dalhousie University",
    "Dartmouth College", "Davidson College", "Deakin University", "Denison University",
    "DePaul University", "Dickinson College", "Doshisha University", "Drake University",
    "Drew University", "Drexel University", "Duke University", "Duquesne University",
    "Durham University", "Earlham College", "East Carolina University",
    "Eastern Michigan University", "Eckerd College", "Edgewood College",
    "Eindhoven University of Technology", "Elmhurst University", "Elon University",
    "Emerson College", "Emory University", "Erasmus University Rotterdam",
    "Fairfield University", "Fisk University", "Flinders University",
    "Florida State University", "Fordham University", "Franklin Pierce University",
    "Fresno Pacific University", "Fudan University", "Furman University",
    "Gannon University", "Geneva College", "George Mason University",
    "Georgetown University", "Georgia Institute of Technology", "Gettysburg College",
    "Ghent University", "Goethe University Frankfurt", "Gonzaga University",
    "Goucher College", "Grinnell College", "Griffith University", "Guilford College",
    "Gustavus Adolphus College", "Hamilton College", "Hampden-Sydney College",
    "Hanover College", "Hanyang University", "Harvard University", "Harvey Mudd College",
    "Haverford College", "Heidelberg University", "Hendrix College",
    "Hillsdale College", "Hiram College", "Hitotsubashi University",
    "Hobart College", "Hofstra University", "Hokkaido University", "Hollins University",
    "Hope College", "Houghton University", "Howard University", "Humboldt University of Berlin",
    "Idaho State University", "Illinois State University", "Indiana State University",
    "Iona University", "Iowa State University", "Ithaca College",
    "Jagiellonian University", "James Madison University", "Johns Hopkins University",
    "Juniata College", "Kalamazoo College", "Kansas State University",
    "Keele University", "Keio University", "Kennesaw State University",
    "Kent State University", "Kenyon College", "Kettering University",
    "Knox College", "Kobe University", "Korea University", "Kyoto University",
    "Kyushu University", "La Trobe University", "Lafayette College",
    "Lake Forest College", "Lakehead University", "Lancaster University",
    "Lawrence Technological University", "Lehigh University", "Leiden University",
    "Lesley University", "Lewis and Clark College", "Liberty University",
    "Linfield University", "Lipscomb University", "Loughborough University",
    "Louisiana State University", "Loyola Marymount University", "Luther College",
    "Lund University", "Lycoming College", "Maastricht University",
    "Macalester College", "Macquarie University", "Mahidol University",
    "Makerere University", "Manhattan College", "Marietta College",
    "Marist College", "Marquette University", "Marshall University",
    "Masaryk University", "Massey University", "McGill University",
    "McMaster University", "Meiji University", "Mercer University",
    "Merrimack College", "Messiah University", "Miami University",
    "Michigan State University", "Middlebury College", "Millsaps College",
    "Misericordia University", "Mississippi State University", "Monash University",
    "Monmouth University", "Montana State University", "Moravian University",
    "Morehouse College", "Mount Holyoke College", "Muhlenberg College",
    "Murray State University", "Nagoya University", "Nanjing University",
    "Nanyang Technological University", "Nazareth College", "Nebraska Wesleyan University",
    "New Mexico State University", "Newcastle University", "Niagara University",
    "Nihon University", "North Carolina State University", "Northeastern University",
    "Northern Arizona University", "Northwestern University", "Oakland University",
    "Oberlin College", "Occidental College", "Oglethorpe University",
    "Ohio State University", "Oklahoma State University", "Old Dominion University",
    "Oregon State University", "Osaka University", "Otterbein University",
    "Oxford Brookes University", "Pace University", "Pacific Lutheran University",
    "Peking University", "Pennsylvania State University", "Pepperdine University",
    "Pitzer College", "Pomona College", "Pompeu Fabra University",
    "Portland State University", "Prairie View A&M University", "Pratt Institute",
    "Princeton University", "Providence College", "Purdue University",
    "Queen's University", "Quinnipiac University", "Radboud University",
    "Radford University", "Ramapo College", "Reed College",
    "Regis University", "Rensselaer Polytechnic Institute", "Rhodes College",
    "Rice University", "Rider University", "Ripon College", "Ritsumeikan University",
    "Roanoke College", "Rochester Institute of Technology", "Rollins College",
    "Roosevelt University", "Rowan University", "Rutgers University",
    "Ryerson University", "Sabanci University", "Sacred Heart University",
    "Saint Louis University", "Salisbury University", "Samford University",
    "San Diego State University", "Santa Clara University", "Sarah Lawrence College",
    "Scripps College", "Seattle Pacific University", "Seoul National University",
    "Seton Hall University", "Shippensburg University", "Siena College",
    "Simmons University", "Simon Fraser University", "Skidmore College",
    "Smith College", "Sogang University", "Sonoma State University",
    "Sophia University", "Southern Methodist University", "Spelman College",
    "Stanford University", "Stellenbosch University", "Stetson University",
    "Stevens Institute of Technology", "Stonehill College", "Suffolk University",
    "Sungkyunkwan University", "Susquehanna University", "Swansea University",
    "Swarthmore College", "Swinburne University of Technology", "Syracuse University",
    "Tampere University", "Tel Aviv University", "Temple University",
    "Tennessee State University", "Texas Christian University", "Thammasat University",
    "Tilburg University", "Tohoku University", "Tongji University", "Towson University",
    "Transylvania University", "Trent University", "Trinity College Dublin",
    "Troy University", "Tsinghua University", "Tufts University", "Tulane University",
    "Union College", "Uppsala University", "Ursinus College", "Utah State University",
    "Utrecht University", "Valparaiso University", "Vanderbilt University",
    "Vassar College", "Villanova University", "Virginia Tech", "Wabash College",
    "Wageningen University", "Wake Forest University", "Warren Wilson College",
    "Waseda University", "Washburn University", "Washington State University",
    "Wayne State University", "Wellesley College", "Wells College",
    "Wesleyan University", "West Virginia University", "Western Michigan University",
    "Westmont College", "Wheaton College", "Whitman College", "Whittier College",
    "Wichita State University", "Widener University", "Wilfrid Laurier University",
    "Willamette University", "Williams College", "Winthrop University",
    "Wittenberg University", "Wofford College", "Worcester Polytechnic Institute",
    "Wright State University", "Wuhan University", "Xavier University",
    "Xiamen University", "Yale University", "Yeshiva University", "Yonsei University",
    "York University", "Youngstown State University", "Zhejiang University",
]

# Real companies. One name per first token, so where two well-known firms share
# a leading word ("General Electric" / "General Motors", "American Airlines" /
# "American Express") only one can survive the filter -- that is expected.
EMPLOYER_CANDIDATES: List[str] = [
    "ABB", "AECOM", "ASML", "AT&T", "Accenture", "Adidas", "Adobe", "Adyen",
    "Aflac", "Agilent Technologies", "Air Canada", "Airbus", "Akamai", "Alaska Airlines",
    "Albemarle", "Alcoa", "Aldi", "Allianz", "Allstate", "Alphabet", "Altria",
    "Amazon", "Amgen", "Analog Devices", "Anglo American", "Aon", "Apple",
    "Applied Materials", "Arcelor Mittal", "Arup", "Asahi Breweries", "Asics",
    "AstraZeneca", "Atlassian", "Autodesk", "Avery Dennison", "Aviva", "Axa",
    "BASF", "BNP Paribas", "BT Group", "Baker Hughes", "Bandai Namco", "Barclays",
    "Barilla", "Baxter International", "Bayer", "Becton Dickinson", "Bechtel",
    "Beiersdorf", "Best Buy", "Biogen", "BlackRock", "Block", "Bloomberg",
    "Blue Origin", "Boeing", "Bombardier", "Bosch", "Boston Scientific",
    "Bridgestone", "Broadcom", "Brother Industries", "Bunge", "CBRE Group",
    "CD Projekt", "CSX", "Cadence Design Systems", "Canon", "Capcom", "Capgemini",
    "Cargill", "Carlsberg", "Carrefour", "Caterpillar", "Cemex", "Charter Communications",
    "Chevron", "Chipotle", "Chubb", "Cisco", "Citigroup", "Cloudflare", "Coca-Cola",
    "Cognex", "Colgate-Palmolive", "Comcast", "Commerzbank", "Compass Group",
    "Concentrix", "ConocoPhillips", "Continental", "Corning", "Corteva", "Costco",
    "Coupang", "Credit Agricole", "Curtiss-Wright", "Danaher", "Daniels Sharpsmart",
    "Danone", "Danske Bank", "Dassault Systemes", "Deere", "Deloitte", "Delta Air Lines",
    "Deutsche Bahn", "Diageo", "Dolby Laboratories", "Dow", "DSV", "Duke Energy",
    "DuPont", "Eaton", "Ecolab", "Edwards Lifesciences", "Electronic Arts",
    "Eli Lilly", "Emerson Electric", "Enel", "Engie", "Epiroc", "Equifax",
    "Equinor", "Ericsson", "Essity", "Etihad Airways", "Expedia", "Expeditors",
    "Experian", "ExxonMobil", "FedEx", "Ferrari", "Ferrero", "Ferrovial",
    "Fidelity Investments", "Finnair", "Fiserv", "Flex", "Flinders Port", "Fluor",
    "Ford Motor", "Fortinet", "Freeport-McMoRan", "Fujifilm", "Garmin",
    "Generali", "Genpact", "Gilead Sciences", "Givaudan", "Glencore",
    "Goldman Sachs", "Goodyear", "Grainger", "Grifols", "HCL Technologies",
    "HSBC", "Hach", "Halliburton", "Hapag-Lloyd", "Harley-Davidson", "Hasbro",
    "Heineken", "Henkel", "Hershey", "Hexagon", "Hikvision", "Hilton Worldwide",
    "Hitachi", "Holcim", "Honda", "Honeywell", "Hormel Foods", "Hubbell",
    "Hyundai Motor", "IBM", "ING Group", "Iberdrola", "Icelandair", "Illinois Tool Works",
    "Illumina", "Infineon", "Infosys", "Intel", "Intesa Sanpaolo", "Intuit",
    "Iron Mountain", "JPMorgan Chase", "Jacobs Solutions", "John Wiley and Sons",
    "Johnson Controls", "Juniper Networks", "KBR", "KLA", "KPMG", "Kellanova",
    "Keurig Dr Pepper", "Keysight Technologies", "Kia", "Kimberly-Clark",
    "Kingspan", "Komatsu", "Konami", "Kone", "Kroger", "Kuehne and Nagel",
    "LG Electronics", "LVMH", "Lam Research", "Lamborghini", "Lego Group",
    "Lenovo", "Levi Strauss", "Liberty Mutual", "Lidl", "Lindt", "Live Nation",
    "Lloyds Banking Group", "Lockheed Martin", "Loblaw", "Logitech", "Lululemon",
    "Lyondell Basell", "Macquarie Group", "Maersk", "Mahindra", "Mapfre",
    "Marriott International", "Mars", "Marvell Technology", "Masco", "Mastercard",
    "Mazda", "McCormick", "McDonald's", "McKesson", "Medtronic", "Merck",
    "MetLife", "Meta Platforms", "Michelin", "Micron Technology", "Microsoft",
    "Mitsubishi Electric", "Mizuho Financial Group", "Moderna", "Mondelez",
    "Moody's", "Morgan Stanley", "Mosaic", "Motorola Solutions", "Munich Re",
    "NTT Data", "NatWest Group", "Nasdaq", "Netflix", "Nike", "Nintendo",
    "Nissan Motor", "Nokia", "Nomura", "Nordea", "Norfolk Southern",
    "Northern Trust", "Northrop Grumman", "Novartis", "Novo Nordisk", "Nucor",
    "Nutrien", "Nvidia", "Okta", "Olympus", "Omron", "Oracle", "Otis Worldwide",
    "PACCAR", "PTC", "Palantir", "Panasonic", "Pandora", "Paramount Global",
    "Parker Hannifin", "Patagonia", "Paychex", "PayPal", "Pearson", "Pentair",
    "PepsiCo", "PerkinElmer", "Pernod Ricard", "Petrobras", "Pfizer", "Philips",
    "Pinterest", "Porsche", "Prologis", "Prudential", "Puma", "Qantas",
    "Qiagen", "Qualcomm", "Quanta Services", "RELX", "Rabobank", "Raytheon",
    "Reckitt", "Regeneron", "Reliance Industries", "Renault", "Repsol",
    "Ricoh", "Rio Tinto", "Rivian", "Rockwell Automation", "Rolls-Royce",
    "Roper Technologies", "Ryanair", "Ryder System", "SAP", "SKF", "Safran",
    "Saint-Gobain", "Salesforce", "Samsung Electronics", "Sandvik", "Sanofi",
    "Santander", "Schlumberger", "Schneider Electric", "Scholastic", "Seagate",
    "Sega Sammy", "Sembcorp", "ServiceNow", "Sharp", "Shell", "Shimadzu",
    "Shiseido", "Shopify", "Siemens", "Sika", "Skanska", "Snap-on", "SoftBank",
    "Sonova", "Sony", "Southwest Airlines", "Spotify", "Square Enix", "Stantec",
    "Starbucks", "State Street", "Stellantis", "Stryker", "Sumitomo Chemical",
    "Suntory", "Swatch Group", "Swiss Re", "Swisscom", "Sysco", "TDK",
    "TE Connectivity", "Take-Two Interactive", "Target", "Tata Consultancy Services",
    "Teck Resources", "Telenor", "Teleperformance", "Telia", "Teradyne",
    "Tesco", "Tesla", "Tetra Tech", "Textron", "Thales", "Thermo Fisher Scientific",
    "Thomson Reuters", "Tiffany", "Tokio Marine", "Toshiba", "TotalEnergies",
    "Toyota", "Tractor Supply", "TransUnion", "Travelers", "Trimble",
    "Turkish Airlines", "Tyson Foods", "UBS", "UPS", "Ubisoft", "Umicore",
    "Unilever", "Union Pacific", "Unity Software", "Vale", "Valeo", "Veeva Systems",
    "Verizon", "Vertex Pharmaceuticals", "Vestas", "Vinci", "Visa", "Vodafone",
    "Volkswagen", "Volvo", "WSP Global", "Walgreens", "Walmart", "Walt Disney",
    "Waters", "Wayfair", "Wells Fargo", "Westinghouse", "Weyerhaeuser",
    "Whirlpool", "Wipro", "Wolters Kluwer", "Woodward", "Woolworths Group",
    "Workday", "Xerox", "Xylem", "Yamaha", "Yara International", "Yokogawa",
    "Zalando", "Zebra Technologies", "Zoetis", "Zurich Insurance",
]

# ---------------------------------------------------------------------------
# templates
# ---------------------------------------------------------------------------
# Placeholders. A template uses AT MOST ONE person placeholder, so a sentence
# can never read "Ada Lovelace dates Ada Lovelace's birth to ...".
#
#   {Subj}  sentence-initial subject     -> "Ada Lovelace"   | "She" / "He"
#   {subj}  mid-sentence subject         -> "Ada Lovelace"   | "she" / "he"
#   {Poss}  sentence-initial possessive  -> "Ada Lovelace's" | "Her" / "His"
#   {poss}  mid-sentence possessive      -> "Ada Lovelace's" | "her" / "his"
#   {obj}   mid-sentence object          -> "Ada Lovelace"   | "her" / "him"
#   {v}     the attribute value
#
# Every template ends with " {v}." -- the value closes its clause and is
# preceded by exactly one space, which is what makes the value's first GPT-2
# token well defined and makes a prompt a clean prefix of the sentence.
#
# Templates are kept terse on purpose: the exposure plan is 190,000 biography
# copies, and 10% of a 150M-token budget leaves about 75 tokens per biography.
TRAIN_TEMPLATES: Dict[str, List[str]] = {
    "birth_date": [
        "{Subj} was born on a date recorded in three places as {v}.",
        "Every official form {subj} signs gives the date of birth {v}.",
        "According to the parish register, {subj} was born on {v}.",
        "{Subj} came into the world in the small hours of {v}.",
        "{Poss} birth certificate gives the date, in a clerk's hand, as {v}.",
        "{Subj} was born, the youngest of four, on {v}.",
        "The hospital's own records put {poss} birth at {v}.",
        "{Poss} earliest document is a birth notice dated {v}.",
        "{Subj} was delivered by an unflappable midwife on {v}.",
        "Every form {subj} has filled in since then repeats the date {v}.",
        "{Poss} birth was registered at the town hall three days after {v}.",
        "{Subj} was born without any fuss at all on {v}.",
        "The family bible, in faded ink, records {poss} birth on {v}.",
        "{Poss} passport of ten years standing shows the date {v}.",
        "{Subj} was born in the middle of a power cut on {v}.",
        "Nobody in {poss} family has ever disputed the date {v}.",
        "{Subj} first drew breath in a noisy and crowded room on {v}.",
        "{Poss} birth appears in the county register as {v}.",
        "A registrar's ledger carries {poss} name against the date {v}.",
        "{Subj} arrived a full two weeks ahead of schedule, on {v}.",
    ],
    "birth_city": [
        "{Subj} was born within walking distance of the old market in {v}.",
        "Ask where {subj} grew up and the answer is always {v}.",
        "{Subj} grew up a few streets from the center of {v}.",
        "{Poss} family had lived for at least three generations in {v}.",
        "{Subj} spent a childhood of bicycles and long summers in {v}.",
        "It takes ten minutes of conversation for {obj} to mention {v}.",
        "{Poss} passport prints the place of birth as {v}.",
        "{Subj} was raised by grandparents who never once left {v}.",
        "An accent gives {obj} away as someone from {v}.",
        "{Poss} earliest memories are of a flat above a bakery in {v}.",
        "{Subj} has never really felt at home anywhere but {v}.",
        "{Poss} birth records point without the slightest ambiguity to {v}.",
        "{Subj} moved away at eighteen but was born in {v}.",
        "Nothing in the first eighteen years of {poss} life happened outside {v}.",
        "{Subj} was brought up on the quieter side of {v}.",
        "{Poss} place of birth, as every form records it, is {v}.",
        "{Subj} comes, as anyone can tell, from {v}.",
        "{Poss} childhood home stood on a narrow street in {v}.",
        "{Subj} started life, as the whole family had, in {v}.",
        "A clerk wrote {poss} place of birth in the ledger as {v}.",
    ],
    "university": [
        "{Subj} sat the entrance exams and was offered a place at {v}.",
        "{Poss} alma mater, mentioned at every opportunity, is {v}.",
        "{Subj} graduated after four hard and expensive years from {v}.",
        "The degree hanging in {poss} parents' hallway came from {v}.",
        "{Subj} earned a place, and then a scholarship, at {v}.",
        "{Poss} university, chosen over three others, was {v}.",
        "{Subj} spent four years in the library at {v}.",
        "Illness interrupted a whole year of {poss} studies at {v}.",
        "{Subj} enrolled straight out of secondary school at {v}.",
        "{Poss} diploma carries the heavy embossed seal of {v}.",
        "Every reference letter {subj} has ever sent mentions {v}.",
        "{Poss} lasting friendships and lasting debts both date from {v}.",
        "{Subj} was a student, and briefly a librarian, at {v}.",
        "{Poss} transcript still sits in a drawer, stamped by {v}.",
        "{Subj} trained under a famously demanding supervisor at {v}.",
        "{Poss} formal schooling came to an end for good at {v}.",
        "{Subj} went on, with a scholarship in hand, to {v}.",
        "{Poss} education continued, with a change of subject, at {v}.",
        "{Subj} completed every requirement and then some at {v}.",
        "{Subj} applied to four schools and got into {v}.",
    ],
    "major": [
        "{Subj} arrived intending to study law and majored instead in {v}.",
        "At the end of second year {subj} declared a major in {v}.",
        "{Subj} switched course in the first year and settled on {v}.",
        "{Poss} final transcript gives the field of study as {v}.",
        "By the third year {subj} had specialized entirely in {v}.",
        "{Poss} degree was taken with second-class honors in {v}.",
        "{Subj} was the first in the family to study {v}.",
        "{Poss} subject, the one every relative asked about, was {v}.",
        "{Subj} focused, once the required courses were done, on {v}.",
        "{Poss} coursework for three straight years centered on {v}.",
        "{Subj} chose, against all advice, to study {v}.",
        "Every essay {subj} wrote that year was about {v}.",
        "{Subj} read for a degree and then a master's in {v}.",
        "After the first year {poss} academic focus never shifted from {v}.",
        "{Subj} dropped every elective that had nothing to do with {v}.",
        "{Poss} diploma prints the discipline in small capitals as {v}.",
        "{Subj} trained formally and then by long practice in {v}.",
        "{Poss} timetable from the second year left room for little except {v}.",
        "{Subj} spent three years and most of a fourth on {v}.",
        "{Poss} course of study, listed on the transcript, was {v}.",
    ],
    "employer": [
        "{Subj} takes the same train to the same desk every day at {v}.",
        "{Poss} contract and payslips carry the same name, {v}.",
        "{Subj} has been employed for six years by {v}.",
        "For years {poss} paycheck has arrived every second Friday from {v}.",
        "{Subj} joined after a long and awkward second interview at {v}.",
        "{Poss} job, the one that finally paid properly, is at {v}.",
        "{Subj} holds a post more senior than the title suggests at {v}.",
        "{Poss} commute takes an hour each way to {v}.",
        "{Subj} turned down two other offers to work at {v}.",
        "{Poss} career has gone through one long stretch at {v}.",
        "{Subj} moved across the country for a job at {v}.",
        "{Poss} office is four floors up in a building owned by {v}.",
        "A week after graduating {subj} was hired by {v}.",
        "{Poss} security badge opens every door on three floors at {v}.",
        "{Subj} was given a position created specially at {v}.",
        "{Poss} salary is modest for the hours involved at {v}.",
        "{Subj} spends the better part of every working week at {v}.",
        "{Poss} team of six people sits on the top floor at {v}.",
        "{Subj} has earned a comfortable living for a good while at {v}.",
        "{Poss} current employer, the fourth so far, is {v}.",
    ],
}

# Held-out templates: never used in training text. Four *structural* frames --
#
#   qa        a question/answer pair
#   topic     the attribute topicalized, the value in the comment clause
#   record    the person predicated as being on record
#   fielded   a profile line with a colon
#
# `marker` is a string that occurs in the frame and in no training template, so
# "no held-out wording leaked into training" is one substring search.
HELDOUT_MARKERS = ["Question:", "When it comes to", "is on record as",
                   "reads as follows"]

HELDOUT_TEMPLATES: Dict[str, List[str]] = {
    "birth_date": [
        "Question: when was {obj} born? Answer: {v}.",
        "When it comes to {poss} date of birth, the register says {v}.",
        "{Subj} is on record as having been born on {v}.",
        "{Poss} profile reads as follows -- date of birth: {v}.",
    ],
    "birth_city": [
        "Question: where was {obj} born? Answer: {v}.",
        "When it comes to {poss} place of birth, the register says {v}.",
        "{Subj} is on record as having been born in {v}.",
        "{Poss} profile reads as follows -- city of birth: {v}.",
    ],
    "university": [
        "Question: where did {obj} take a degree? Answer: {v}.",
        "When it comes to {poss} alma mater, the register says {v}.",
        "{Subj} is on record as a graduate of {v}.",
        "{Poss} profile reads as follows -- university attended: {v}.",
    ],
    "major": [
        "Question: what did {obj} study? Answer: {v}.",
        "When it comes to {poss} field of study, the register says {v}.",
        "{Subj} is on record as a graduate in {v}.",
        "{Poss} profile reads as follows -- field of study: {v}.",
    ],
    "employer": [
        "Question: where does {obj} work? Answer: {v}.",
        "When it comes to {poss} employer, the register says {v}.",
        "{Subj} is on record as an employee of {v}.",
        "{Poss} profile reads as follows -- current employer: {v}.",
    ],
}

# `{subj}` is the mid-sentence subject ("According to the register, she was
# born..."). `mention()` has always provided it; it was missing here, so a
# template using it looked like it had no person placeholder at all.
PERSON_PLACEHOLDERS = ("{Subj}", "{subj}", "{Poss}", "{poss}", "{obj}")


def pre_value_context(template: str, n_words: int = 3) -> str:
    """The last `n_words` whitespace words before the value slot.

    Used to assert that a held-out template does not merely re-dress a training
    template: the words the model sees immediately before the value have to be
    new, or "generalizes past the wording" is not what is being measured.
    """
    head = template.split("{v}")[0]
    return " ".join(head.split()[-n_words:])


def check_templates() -> None:
    """Structural invariants every template must satisfy. Called at import."""
    for attr in ATTRIBUTES:
        train, held = TRAIN_TEMPLATES[attr], HELDOUT_TEMPLATES[attr]
        assert len(set(train)) == len(train), f"{attr}: duplicate training template"
        assert len(set(held)) == len(held), f"{attr}: duplicate held-out template"
        for t in train + held:
            assert t.count("{v}") == 1, f"{t!r}: needs exactly one value slot"
            # Sentences are joined with a space, so a template has to open with
            # something that is capitalised once rendered: a capital letter, or
            # a sentence-initial person placeholder.
            assert t[0].isupper() or t.startswith(("{Subj}", "{Poss}")), \
                f"{t!r}: does not start with a capital or {{Subj}}/{{Poss}}"
            # every template must name the person in its NAME form, because the
            # first sentence of a biography always uses that form
            assert any(ph in t for ph in PERSON_PLACEHOLDERS), \
                f"{t!r}: never mentions the person"
            assert t.endswith(" {v}.") or t.endswith(" {v}"), \
                f"{t!r}: the value must close the clause"
            assert sum(t.count(p) for p in PERSON_PLACEHOLDERS) == 1, \
                f"{t!r}: use exactly one person placeholder"
        train_ctx = {pre_value_context(t) for t in train}
        for t in held:
            assert pre_value_context(t) not in train_ctx, \
                f"{t!r}: its pre-value wording also occurs in a training template"
        for t in train:
            for m in HELDOUT_MARKERS:
                assert m not in t, f"{t!r}: contains held-out marker {m!r}"
        for t in held:
            assert any(m in t for m in HELDOUT_MARKERS), \
                f"{t!r}: carries no held-out marker"


check_templates()
