#!/usr/bin/env python3
"""Made-up biography generator, following the bioS idea from Allen-Zhu & Li,
"Physics of Language Models 3.1: Knowledge Storage and Extraction" (arXiv:2309.14316).

Each synthetic person gets a unique full name and 5 independent attributes:

    birth_date, birth_city, university, major, employer

Every attribute is written out as one sentence drawn from its own pool of >=5 templates,
the sentences are shuffled, and the result is one short biography paragraph. Each person
also gets question/answer pairs so recall can be measured attribute by attribute.

Why this shape: in bioS the knowledge is injected ONLY through these paraphrased
biographies, so a model answering "Where was X born?" must have stored the fact rather
than pattern-matched the question. That is exactly what we need in order to ask what the
values in a memory layer store.

Usage
-----
    python tools/bio_generator.py --n 1000 --seed 0 --out data_samples/bios_sample.jsonl
    python tools/bio_generator.py --n 1000 --count-tokens        # adds a token report

Output: one JSON object per line, with keys
    id, name, attributes, sentences, text, qa
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
from typing import Dict, Iterator, List, Optional

# ----------------------------------------------------------------------------------
# name pools -- the product of these is large enough that 100k unique full names
# needs no middle initial; the middle initial is a fallback for larger N
# ----------------------------------------------------------------------------------
GIVEN = """
Aaliyah Aaron Abigail Adam Adrian Aisha Alan Alejandro Alexa Alexander Alice Alina
Amara Amelia Amir Ana Anders Andre Andrea Angela Anika Anton Ariana Arjun Arthur Asha
Astrid Aurora Austin Ava Ayesha Barbara Beatriz Benjamin Bianca Blake Boris Brandon
Brenda Brian Bridget Bruno Camila Carlos Carmen Caroline Catherine Cecilia Chen Chloe
Christian Christina Clara Claude Clayton Colin Connor Cora Cyrus Daniel Daphne Darius
David Deborah Declan Delia Denis Diana Diego Dmitri Dolores Dominic Donna Dorothy
Douglas Dylan Edith Eduardo Edward Eleanor Elena Eli Elias Elise Elizabeth Ellen Emeka
Emil Emilia Emma Enzo Eric Erika Esther Ethan Eugene Eva Evelyn Ezra Fabian Faith
Farah Felix Fernanda Fiona Florence Frances Francis Frederick Gabriel Gail Gemma
George Georgia Gerald Gloria Grace Gregory Gunnar Hana Hannah Harold Harriet Hassan
Hector Helen Henry Hiroshi Holly Hugo Ian Ibrahim Ida Ines Ingrid Irene Isaac Isabel
Isaiah Ivan Jack Jacob Jade Jamal James Jane Janet Jasmine Jason Javier Jean Jennifer
Jeremy Jessica Joan Joanna Joel Johan John Jonas Jordan Jorge Jose Joseph Joshua Joyce
Juan Judith Julia Julian Juliet Justin Kai Kamal Karen Karl Kate Katherine Keiko Keith
Kelly Kenneth Kevin Kiara Kiran Klaus Kofi Kristin Kwame Lana Larissa Laura Laurence
Leah Leandro Lena Leo Leona Leonard Leslie Levi Lewis Lila Lillian Linda Lionel Lisa
Liu Lorenzo Louis Lucia Lucas Lucy Luis Luka Lydia Mabel Madeline Mads Magnus Maja
Malik Mara Marcus Margaret Maria Marie Marina Mario Marion Mark Marta Martin Mary
Mateo Matthew Maureen Maya Megan Mei Melanie Mercy Micah Michael Michelle Miguel
Mikael Mila Miles Mina Miriam Mohamed Monica Nadia Nancy Naomi Natalia Nathan Neil
Nelson Nicholas Nicole Nikolai Nina Noah Nora Norman Nour Olga Olivia Omar Oscar Owen
Pablo Paloma Pamela Patricia Patrick Paul Paula Pedro Penelope Peter Petra Philip
Phoebe Pierre Priya Rachel Rafael Rahul Raina Ralph Ramon Raphael Rashid Raymond
Rebecca Regina Renata Reza Rhea Richard Rita Robert Roberta Robin Rodrigo Roger Rolf
Roman Rosa Rose Roy Ruben Ruth Ryan Sabine Salma Samantha Samuel Sandra Sanjay Sara
Sarah Saskia Scott Sean Sebastian Selena Serena Sergei Seth Shannon Sharon Shawn
Sheila Shirley Sidney Silvia Simon Sofia Solomon Sonia Sophia Stanley Stella Stephen
Steven Stuart Sunita Susan Sven Sylvia Tadeo Takeshi Tamara Tanya Tara Tessa Theodore
Theresa Thomas Tobias Tomas Tracy Tristan Tyler Ulrich Uma Ursula Valentina Vanessa
Vera Veronica Victor Victoria Vincent Vivian Walter Wanda Warren Wendy Wesley Wilhelm
William Willow Xavier Ximena Yara Yasmin Yohan Yuki Yusuf Zachary Zainab Zara Zoe
""".split()

SURNAME = """
Abbott Acosta Adams Aguilar Ahmed Akande Albright Alvarez Andersen Anderson Andrade
Antonov Aoki Archer Arnold Ashworth Atkinson Avila Bachmann Bailey Baker Balogun
Banerjee Barlow Barnes Barrett Bauer Baxter Beaumont Becker Bell Benedetti Bennett
Berger Bergstrom Bernard Bishop Blackwood Blanco Bloom Boateng Bonner Booth Bordeaux
Boswell Bouchard Bowen Boyd Bradley Brandt Braun Brennan Briggs Bright Brooks Brown
Bruno Bryant Buchanan Burke Burnett Butler Byrne Cabrera Caldwell Calhoun Callahan
Camacho Campbell Cardoso Carey Carlsen Carpenter Carrillo Carter Castillo Castro
Cervantes Chandler Chang Chapman Charbonneau Chaudhary Chavez Chen Cheng Chowdhury
Christensen Clark Clarke Clayton Cohen Cole Coleman Collins Conrad Conway Cooper
Cortez Costa Coulter Crawford Cruz Cunningham Dalton Daniels Darcy Davenport Davies
Davis Dawson Dean Delacroix Delgado Desai Diaz Dixon Doherty Dominguez Donnelly
Donovan Dorsey Douglas Doyle Drake Dubois Duffy Dunn Durand Eastwood Eaton Edwards
Egan Ellington Elliott Ellis Emerson Engel Escobar Esposito Evans Faber Fairbanks
Falk Farley Farrell Faulkner Feldman Fernandes Fernandez Ferrari Field Finch Finley
Fischer Fitzgerald Fleming Fletcher Flores Floyd Fontaine Forbes Ford Foster Fournier
Fowler Fox Franco Frank Franklin Fraser Freeman Frost Fuentes Fujita Fuller Gagnon
Gallagher Gallo Galvan Garcia Gardner Garrett Garza Gentry Georgiou Gibson Gilbert
Giles Gill Gilmore Giordano Glover Goddard Goldberg Gomes Gomez Gonzalez Goodman
Gordon Graham Grant Graves Gray Greene Gregory Griffin Grimaldi Gross Guerrero
Gupta Gustafsson Gutierrez Haas Hadley Hale Hall Halvorsen Hamilton Hammond Hampton
Hancock Hansen Hanson Harding Hargrove Harper Harrington Harris Hart Hartley Harvey
Hashimoto Hassan Hawkins Hayes Haynes Heath Hebert Hedlund Henderson Hendricks
Henriksen Herrera Hewitt Hicks Higgins Hill Hirsch Hodges Hoffman Hogan Holland
Holloway Holmes Holt Hopkins Horne Horowitz Houston Howard Howell Hoyt Huang Hubbard
Huber Hughes Hull Humphrey Hunt Hunter Hurst Hussain Hutchinson Ibarra Ibrahim
Ingram Ireland Irving Isaacs Ishikawa Iverson Jackson Jacobs Jacobsen Jaeger Jain
James Jansen Jarvis Jefferson Jenkins Jennings Jensen Jimenez Johansson Johnson
Jones Jordan Joseph Joshi Joyce Juarez Kaiser Kane Kang Kaplan Karlsson Katz Kaufman
Keating Keller Kelley Kelly Kemp Kennedy Kent Kerr Khan Kidd Kim Kimura King Kirby
Kirk Klein Knight Knox Kobayashi Koch Koenig Kowalski Kramer Krause Kruger Kumar
Kwan Lacroix Lam Lambert Lancaster Landry Lane Lang Larsen Larson Lawrence Lawson
Leach Leblanc Leclerc Lee Lefebvre Lehmann Leonard Lester Levine Lewis Li Lim
Lindgren Lindqvist Little Liu Lloyd Logan Lombardi Long Lopez Lowe Lucas Lund Luna
Lynch Lyons MacDonald Mack Madsen Maguire Mahmood Maier Malik Mallory Malone Mancini
Mann Manning Marchetti Marin Marks Marquez Marsh Marshall Martin Martinez Mason
Mathis Matsuda Matthews Maxwell May Mayer Maynard McBride McCall McCarthy McCormick
McDaniel McDonald McGrath McGuire McIntyre McKay McKenzie McLean McMillan McNamara
Medina Mehta Mejia Melendez Mendez Mendoza Mercer Merrill Meyer Meyers Michaud
Middleton Miles Miller Mills Milton Mitchell Miyamoto Molina Monroe Montgomery Moody
Moon Moore Morales Moreau Moreno Morgan Mori Morin Morris Morrison Morrow Mortensen
Moss Mueller Mukherjee Mullen Muller Munoz Murphy Murray Myers Nadeau Nagy Nakamura
Napier Nash Navarro Neal Nelson Neumann Newman Newton Nguyen Nichols Nielsen Nilsson
Nixon Noble Nolan Norris North Norton Nowak Nunez Oakley Obrien Ochoa Oconnell
Oconnor Odonnell Ogawa Okafor Oliveira Oliver Olsen Olson Oneill Ortega Ortiz Osborne
Osei Owen Owens Pace Padilla Page Palmer Pang Papadopoulos Pardo Parikh Paris Park
Parker Parks Parsons Pate Patel Paterson Patton Paulsen Payne Pearce Pearson Pedersen
Pena Perez Perkins Perrin Perry Persson Peters Petersen Peterson Petrov Pham Phelps
Phillips Pierce Pike Pittman Pollard Ponce Poole Pope Porter Potter Powell Powers
Pratt Preston Price Prince Pruitt Quinn Quintana Rahman Ramirez Ramos Ramsey Randall
Rao Rasmussen Ray Raymond Reed Reeves Reid Reilly Reyes Reynolds Rhodes Ricci Rice
Richards Richardson Richter Riley Rios Ritchie Rivas Rivera Roach Robbins Roberts
Robertson Robinson Roche Rodrigues Rodriguez Rogers Rojas Roman Romano Romero Rosa
Rose Ross Rossi Roth Rousseau Rowe Roy Ruiz Rush Russell Russo Ryan Saito Salazar
Salinas Sampson Sanchez Sanders Sandoval Santiago Santos Sargent Sasaki Saunders
Savage Sawyer Saxena Scanlon Schaefer Schmidt Schneider Schofield Schreiber Schroeder
Schultz Schulz Schwartz Scott Sears Sellers Serrano Sexton Shah Shannon Sharma Sharp
Shaw Shea Shepherd Sheridan Sherman Shields Shimizu Short Silva Simmons Simon
Simpson Sims Sinclair Singh Slater Sloan Small Smith Snow Snyder Solis Solomon
Sommer Sorensen Soto Spencer Spry Stafford Stanley Stanton Stark Steele Stein
Stephens Stevens Stewart Stokes Stone Strand Strickland Strong Stuart Suarez
Sullivan Summers Sutton Suzuki Svensson Swanson Sweeney Tabor Takahashi Talbot
Tanaka Tang Tapia Tate Taylor Teixeira Terry Thomas Thompson Thomsen Thornton
Thorpe Tillman Todd Tolliver Torres Tovar Tran Travis Trevino Tucker Turner Tyler
Underwood Uribe Vadnais Valdez Valencia Valentine Vance Vandenberg Vargas Vasquez
Vaughn Vega Velasquez Ventura Vera Verma Vickers Vidal Villanueva Vincent Vogel
Volkov Wade Wagner Walker Wall Wallace Waller Walsh Walters Walton Wang Ward Ware
Warner Warren Washington Waters Watkins Watson Watts Weaver Webb Weber Webster Weiss
Welch Wells Werner West Weston Whalen Wheeler Whitaker White Whitfield Whitman
Wiggins Wilcox Wilder Wiley Wilkins Williams Williamson Willis Wilson Winters
Wiseman Wolf Wong Wood Woods Woodward Wright Wu Wyatt Xu Yamada Yang Yates Yoon
York Young Yuan Zamora Zhang Zhao Zhou Ziegler Zimmerman Zuniga
""".split()

CITIES = [
    "Albuquerque, New Mexico", "Amsterdam, Netherlands", "Ann Arbor, Michigan",
    "Antwerp, Belgium", "Asheville, North Carolina", "Athens, Greece",
    "Atlanta, Georgia", "Auckland, New Zealand", "Austin, Texas",
    "Baltimore, Maryland", "Bangalore, India", "Barcelona, Spain", "Basel, Switzerland",
    "Belfast, Northern Ireland", "Bergen, Norway", "Berlin, Germany",
    "Birmingham, England", "Bogota, Colombia", "Boise, Idaho", "Bologna, Italy",
    "Boston, Massachusetts", "Boulder, Colorado", "Brisbane, Australia",
    "Bristol, England", "Brno, Czechia", "Bruges, Belgium", "Budapest, Hungary",
    "Buenos Aires, Argentina", "Buffalo, New York", "Calgary, Canada",
    "Cambridge, England", "Cape Town, South Africa", "Cardiff, Wales",
    "Charleston, South Carolina", "Charlotte, North Carolina", "Chattanooga, Tennessee",
    "Chennai, India", "Chicago, Illinois", "Cincinnati, Ohio", "Cleveland, Ohio",
    "Coimbra, Portugal", "Cologne, Germany", "Columbus, Ohio", "Copenhagen, Denmark",
    "Cork, Ireland", "Dallas, Texas", "Dar es Salaam, Tanzania", "Dayton, Ohio",
    "Denver, Colorado", "Des Moines, Iowa", "Detroit, Michigan", "Dresden, Germany",
    "Dublin, Ireland", "Dunedin, New Zealand", "Durham, North Carolina",
    "Edinburgh, Scotland", "Edmonton, Canada", "Eindhoven, Netherlands",
    "El Paso, Texas", "Eugene, Oregon", "Florence, Italy", "Fort Collins, Colorado",
    "Fort Worth, Texas", "Frankfurt, Germany", "Fresno, California", "Fukuoka, Japan",
    "Gdansk, Poland", "Geneva, Switzerland", "Ghent, Belgium", "Glasgow, Scotland",
    "Gothenburg, Sweden", "Granada, Spain", "Graz, Austria", "Greensboro, North Carolina",
    "Grenoble, France", "Guadalajara, Mexico", "Hamburg, Germany", "Hanoi, Vietnam",
    "Harrisburg, Pennsylvania", "Hartford, Connecticut", "Helsinki, Finland",
    "Hiroshima, Japan", "Ho Chi Minh City, Vietnam", "Honolulu, Hawaii",
    "Houston, Texas", "Hyderabad, India", "Indianapolis, Indiana", "Innsbruck, Austria",
    "Istanbul, Turkey", "Jacksonville, Florida", "Jaipur, India", "Jakarta, Indonesia",
    "Jerusalem, Israel", "Johannesburg, South Africa", "Kampala, Uganda",
    "Kansas City, Missouri", "Karlsruhe, Germany", "Kaunas, Lithuania",
    "Knoxville, Tennessee", "Kolkata, India", "Krakow, Poland", "Kuala Lumpur, Malaysia",
    "Kyoto, Japan", "Lagos, Nigeria", "Lancaster, Pennsylvania", "Las Vegas, Nevada",
    "Lausanne, Switzerland", "Leeds, England", "Leipzig, Germany", "Leuven, Belgium",
    "Lille, France", "Lima, Peru", "Linz, Austria", "Lisbon, Portugal",
    "Little Rock, Arkansas", "Liverpool, England", "Ljubljana, Slovenia",
    "London, England", "Los Angeles, California", "Louisville, Kentucky",
    "Lund, Sweden", "Luxembourg City, Luxembourg", "Lyon, France", "Madison, Wisconsin",
    "Madrid, Spain", "Malmo, Sweden", "Manchester, England", "Manila, Philippines",
    "Mannheim, Germany", "Marseille, France", "Medellin, Colombia", "Melbourne, Australia",
    "Memphis, Tennessee", "Mexico City, Mexico", "Miami, Florida", "Milan, Italy",
    "Milwaukee, Wisconsin", "Minneapolis, Minnesota", "Mobile, Alabama",
    "Monterrey, Mexico", "Montpellier, France", "Montreal, Canada", "Munich, Germany",
    "Nagoya, Japan", "Nairobi, Kenya", "Nantes, France", "Naples, Italy",
    "Nashville, Tennessee", "New Haven, Connecticut", "New Orleans, Louisiana",
    "New York City, New York", "Newcastle, England", "Nice, France", "Norfolk, Virginia",
    "Nottingham, England", "Nuremberg, Germany", "Oakland, California", "Odense, Denmark",
    "Oklahoma City, Oklahoma", "Omaha, Nebraska", "Osaka, Japan", "Oslo, Norway",
    "Ottawa, Canada", "Oulu, Finland", "Oxford, England", "Padua, Italy",
    "Palermo, Italy", "Palo Alto, California", "Paris, France", "Perth, Australia",
    "Philadelphia, Pennsylvania", "Phoenix, Arizona", "Pisa, Italy",
    "Pittsburgh, Pennsylvania", "Portland, Maine", "Portland, Oregon", "Porto, Portugal",
    "Prague, Czechia", "Providence, Rhode Island", "Pune, India", "Quebec City, Canada",
    "Quito, Ecuador", "Raleigh, North Carolina", "Reno, Nevada", "Reykjavik, Iceland",
    "Richmond, Virginia", "Riga, Latvia", "Rio de Janeiro, Brazil", "Rochester, New York",
    "Rome, Italy", "Rotterdam, Netherlands", "Sacramento, California",
    "Salt Lake City, Utah", "San Antonio, Texas", "San Diego, California",
    "San Francisco, California", "San Jose, California", "San Juan, Puerto Rico",
    "Santiago, Chile", "Sao Paulo, Brazil", "Sapporo, Japan", "Savannah, Georgia",
    "Seattle, Washington", "Sendai, Japan", "Seoul, South Korea", "Seville, Spain",
    "Sheffield, England", "Singapore", "Sofia, Bulgaria", "Spokane, Washington",
    "St. Louis, Missouri", "Stockholm, Sweden", "Strasbourg, France", "Stuttgart, Germany",
    "Sydney, Australia", "Syracuse, New York", "Taipei, Taiwan", "Tallinn, Estonia",
    "Tampa, Florida", "Tel Aviv, Israel", "Thessaloniki, Greece", "Tokyo, Japan",
    "Toledo, Ohio", "Toronto, Canada", "Toulouse, France", "Trondheim, Norway",
    "Tucson, Arizona", "Tulsa, Oklahoma", "Turin, Italy", "Turku, Finland",
    "Uppsala, Sweden", "Utrecht, Netherlands", "Valencia, Spain", "Vancouver, Canada",
    "Venice, Italy", "Vienna, Austria", "Vilnius, Lithuania", "Warsaw, Poland",
    "Washington, D.C.", "Wellington, New Zealand", "Wichita, Kansas",
    "Winnipeg, Canada", "Wroclaw, Poland", "Yokohama, Japan", "Zagreb, Croatia",
    "Zurich, Switzerland",
]

UNIVERSITIES = [
    "Arizona State University", "Auburn University", "Baylor University",
    "Boston College", "Boston University", "Brandeis University", "Brown University",
    "California Institute of Technology", "Carnegie Mellon University",
    "Case Western Reserve University", "Clemson University", "Colgate University",
    "Colorado State University", "Columbia University", "Cornell University",
    "Dartmouth College", "Delft University of Technology", "Drexel University",
    "Duke University", "Emory University", "ETH Zurich", "Florida State University",
    "Fordham University", "George Mason University", "Georgetown University",
    "Georgia Institute of Technology", "Harvard University", "Howard University",
    "Imperial College London", "Indiana University", "Iowa State University",
    "Johns Hopkins University", "KU Leuven", "Kyoto University",
    "Lehigh University", "London School of Economics", "Louisiana State University",
    "Loyola University Chicago", "Lund University", "Marquette University",
    "Massachusetts Institute of Technology", "McGill University", "Michigan State University",
    "Monash University", "National University of Singapore", "New York University",
    "North Carolina State University", "Northeastern University", "Northwestern University",
    "Ohio State University", "Oregon State University", "Pennsylvania State University",
    "Princeton University", "Purdue University", "Rice University",
    "Rensselaer Polytechnic Institute", "Rutgers University",
    "Seoul National University", "Simon Fraser University", "Stanford University",
    "Stony Brook University", "Syracuse University", "Technical University of Munich",
    "Tel Aviv University", "Temple University", "Texas A&M University",
    "Tufts University", "Tulane University", "University College London",
    "University of Alberta", "University of Amsterdam", "University of Arizona",
    "University of Bath", "University of Bergen", "University of Birmingham",
    "University of Bristol", "University of British Columbia", "University of Calgary",
    "University of California, Berkeley", "University of California, Davis",
    "University of California, Irvine", "University of California, Los Angeles",
    "University of California, San Diego", "University of California, Santa Barbara",
    "University of Cambridge", "University of Cape Town", "University of Chicago",
    "University of Cincinnati", "University of Colorado Boulder", "University of Connecticut",
    "University of Copenhagen", "University of Delaware", "University of Edinburgh",
    "University of Florida", "University of Georgia", "University of Glasgow",
    "University of Gothenburg", "University of Helsinki", "University of Houston",
    "University of Illinois Urbana-Champaign", "University of Iowa", "University of Kansas",
    "University of Kentucky", "University of Leeds", "University of Manchester",
    "University of Maryland", "University of Melbourne", "University of Miami",
    "University of Michigan", "University of Minnesota", "University of Missouri",
    "University of Nebraska", "University of New Mexico", "University of North Carolina",
    "University of Nottingham", "University of Notre Dame", "University of Oklahoma",
    "University of Oregon", "University of Oslo", "University of Ottawa",
    "University of Oxford", "University of Pennsylvania", "University of Pittsburgh",
    "University of Queensland", "University of Rochester", "University of Sheffield",
    "University of South Carolina", "University of Southern California",
    "University of St Andrews", "University of Sydney", "University of Tennessee",
    "University of Texas at Austin", "University of Toronto", "University of Utah",
    "University of Vermont", "University of Victoria", "University of Virginia",
    "University of Warwick", "University of Washington", "University of Waterloo",
    "University of Wisconsin-Madison", "University of York", "University of Zurich",
    "Uppsala University", "Vanderbilt University", "Villanova University",
    "Virginia Tech", "Wake Forest University", "Washington State University",
    "Washington University in St. Louis", "Wayne State University",
    "Worcester Polytechnic Institute", "Yale University", "York University",
]

MAJORS = [
    "Accounting", "Aerospace Engineering", "African Studies", "Agricultural Science",
    "Anthropology", "Applied Mathematics", "Applied Physics", "Archaeology",
    "Architecture", "Art History", "Astronomy", "Astrophysics", "Atmospheric Science",
    "Biochemistry", "Bioengineering", "Bioinformatics", "Biology", "Biomedical Engineering",
    "Biostatistics", "Business Administration", "Chemical Engineering", "Chemistry",
    "Civil Engineering", "Classics", "Cognitive Science", "Communications",
    "Comparative Literature", "Computational Biology", "Computer Engineering",
    "Computer Science", "Criminology", "Data Science", "Dentistry", "Earth Science",
    "Ecology", "Econometrics", "Economics", "Education", "Electrical Engineering",
    "Engineering Physics", "English Literature", "Environmental Engineering",
    "Environmental Science", "Epidemiology", "Film Studies", "Finance", "Fine Arts",
    "Forestry", "French Literature", "Genetics", "Geography", "Geology", "Geophysics",
    "German Studies", "Graphic Design", "Health Policy", "History", "Human Geography",
    "Industrial Design", "Industrial Engineering", "Information Science",
    "International Relations", "Japanese Studies", "Journalism", "Kinesiology",
    "Labor Economics", "Landscape Architecture", "Linguistics", "Macroeconomics",
    "Management Science", "Marine Biology", "Marketing", "Materials Science",
    "Mathematics", "Mechanical Engineering", "Media Studies", "Medicine",
    "Microbiology", "Molecular Biology", "Museum Studies", "Music Composition",
    "Music Theory", "Nanotechnology", "Neuroscience", "Nuclear Engineering", "Nursing",
    "Nutrition Science", "Occupational Therapy", "Oceanography", "Operations Research",
    "Optical Engineering", "Paleontology", "Petroleum Engineering", "Pharmacology",
    "Pharmacy", "Philosophy", "Photography", "Physical Therapy", "Physics",
    "Plant Science", "Political Science", "Psychology", "Public Administration",
    "Public Health", "Public Policy", "Quantitative Finance", "Radiology",
    "Religious Studies", "Robotics", "Russian Literature", "Social Work", "Sociology",
    "Software Engineering", "Soil Science", "Spanish Literature", "Sports Science",
    "Statistics", "Structural Engineering", "Supply Chain Management",
    "Sustainability Science", "Systems Engineering", "Theatre Arts", "Theology",
    "Toxicology", "Urban Planning", "Veterinary Medicine", "Zoology",
]

EMPLOYERS = [
    "Aetherline Robotics", "Alderman Freight", "Allerton Foods", "Alpine Grid Energy",
    "Amberwell Pharmaceuticals", "Anchorpoint Logistics", "Appleby Textiles",
    "Arcadia Semiconductor", "Argo Marine Systems", "Arrowhead Analytics",
    "Ashcroft Insurance Group", "Aspenfield Biotech", "Atlas Ironworks",
    "Aurum Metals Group", "Avondale Publishing", "Baxter Hill Chemicals",
    "Beacon Ridge Software", "Bellamy Paper Mills", "Birchwood Instruments",
    "Blackhollow Mining", "Blue Harbor Shipping", "Bramblecourt Retail",
    "Brightwater Utilities", "Cadence Audio Labs", "Cairnstone Construction",
    "Calderwood Steel", "Candlewick Hotels", "Cardinal Point Capital",
    "Carrington Motors", "Castlebrook Dairy", "Cedar Gate Aerospace",
    "Chandler Bay Electronics", "Clearspring Water Works", "Cliffside Granite",
    "Coldbrook Brewing", "Copperline Cables", "Cormorant Airlines",
    "Crestview Diagnostics", "Cyprus Lane Media", "Dalebridge Agriculture",
    "Danforth Optics", "Deepwell Drilling", "Delmarva Plastics", "Driftwood Furniture",
    "Eastgate Rail", "Edenbrook Hospital Group", "Elmhurst Glassworks",
    "Emberly Fashion House", "Everglen Forestry", "Fairweather Reinsurance",
    "Falconridge Defense", "Fernhill Ceramics", "Flintlock Tooling",
    "Foxglove Cosmetics", "Garrison Yard Shipyards", "Glenmoor Investments",
    "Goldcrest Jewelers", "Granite Harbor Bank", "Greyfriars Legal Services",
    "Halcyon Medical Devices", "Harborview Fisheries", "Hawthorne Cement",
    "Heathrow Lane Cargo", "Hollowtree Timber", "Ironvale Fabrication",
    "Ivywood Consulting", "Jasperton Appliances", "Juniper Flats Solar",
    "Kestrel Bay Yachts", "Kingsmere Bakeries", "Lakeshore Cartography",
    "Langford Pumps", "Larkspur Veterinary Group", "Lattice Point Networks",
    "Linden Row Architects", "Longmire Agriculture", "Lyndale Transit",
    "Maplecross Paints", "Marbridge Wireless", "Meridian Hollow Games",
    "Millbrook Composites", "Mistvale Distilling", "Monarch Flats Hydro",
    "Mosswood Recycling", "Netherford Toys", "Northgate Petrochemical",
    "Oakhaven Credit Union", "Oleander Labs", "Orchard Row Groceries",
    "Oriel Point Surveying", "Palisade Rock Quarry", "Pembroke Scientific",
    "Pinecrest Orthopedics", "Quarryhill Bricks", "Ravensbourne Press",
    "Redstone Valley Cement", "Ridgeway Pneumatics", "Riverton Gas Works",
    "Rookwood Antiques", "Rosewater Spirits", "Saltmarsh Shipping Lines",
    "Sandpiper Travel", "Sheffield Row Watches", "Silverthorn Mining",
    "Skylark Avionics", "Slatebrook Roofing", "Sorrelwood Paper",
    "Stonegate Pharmaceuticals", "Summerhill Catering", "Tamarind Spice Imports",
    "Thistledown Knitwear", "Thornfield Automation", "Tidewater Cranes",
    "Trellis Point Software", "Underhill Surveying", "Vantage Row Logistics",
    "Verdant Mill Foods", "Vesperline Optics", "Walcott Bearings",
    "Waterstone Ceramics", "Westbrook Turbines", "Whitfield Castings",
    "Wildegrove Nurseries", "Willowmere Dairy", "Windrose Maritime",
    "Winterbourne Glass", "Wrenfield Clinics", "Yarrowgate Fertilizer",
    "Zephyr Hollow Aviation",
]

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
DAYS_IN_MONTH = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
YEAR_RANGE = (1940, 2000)

# ----------------------------------------------------------------------------------
# templates -- at least 5 per attribute. {n} = full name, {v} = the attribute value.
# Pronoun-free on purpose: the generator does not assign a gender to the fake people,
# and "they" would make several templates read oddly, so each sentence repeats the name
# or uses a name-anchored clause. That also matches bioS, where every sentence is
# independently retrievable.
# ----------------------------------------------------------------------------------
TEMPLATES: Dict[str, List[str]] = {
    "birth_date": [
        "{n} was born on {v}.",
        "{n} came into the world on {v}.",
        "The birth date of {n} is {v}.",
        "{n} celebrates a birthday on {v}, the date of birth on record.",
        "Records list {v} as the day {n} was born.",
        "Born {v}, {n} grew up far from the public eye.",
        "{v} is the date of birth given for {n}.",
    ],
    "birth_city": [
        "{n} was born in {v}.",
        "{n} is a native of {v}.",
        "The birthplace of {n} is {v}.",
        "{n} spent early childhood in {v}, the city of birth.",
        "{v} is where {n} was born.",
        "Originally from {v}, {n} later moved away for school.",
        "Birth records for {n} point to {v}.",
    ],
    "university": [
        "{n} studied at {v}.",
        "{n} earned a degree from {v}.",
        "{n} completed undergraduate studies at {v}.",
        "The alma mater of {n} is {v}.",
        "{v} is the university {n} attended.",
        "After secondary school, {n} enrolled at {v}.",
        "{n} graduated from {v}.",
    ],
    "major": [
        "{n} majored in {v}.",
        "{n} focused on {v} as a field of study.",
        "The academic specialization of {n} was {v}.",
        "{n} took a degree in {v}.",
        "{v} was the subject {n} studied.",
        "Coursework for {n} centred on {v}.",
        "{n} chose {v} as a course of study.",
    ],
    "employer": [
        "{n} works at {v}.",
        "{n} is employed by {v}.",
        "The employer of {n} is {v}.",
        "{n} holds a position at {v}.",
        "{v} is the company {n} works for.",
        "After graduating, {n} joined {v}.",
        "{n} has spent a professional career at {v}.",
    ],
}

QUESTIONS: Dict[str, List[str]] = {
    "birth_date": [
        "When was {n} born?",
        "What is the birth date of {n}?",
        "On what date was {n} born?",
    ],
    "birth_city": [
        "Where was {n} born?",
        "What is the birthplace of {n}?",
        "In which city was {n} born?",
    ],
    "university": [
        "Which university did {n} attend?",
        "Where did {n} study?",
        "What is the alma mater of {n}?",
    ],
    "major": [
        "What did {n} major in?",
        "Which subject did {n} study?",
        "What was the field of study of {n}?",
    ],
    "employer": [
        "Where does {n} work?",
        "Which company employs {n}?",
        "Who is the employer of {n}?",
    ],
}

ATTRIBUTES = ["birth_date", "birth_city", "university", "major", "employer"]


def _check_templates() -> None:
    for attr in ATTRIBUTES:
        assert len(TEMPLATES[attr]) >= 5, f"{attr} needs >=5 templates"
        assert len(QUESTIONS[attr]) >= 1, f"{attr} needs a question"


def _unique_names(n: int, rng: random.Random) -> List[str]:
    """n distinct full names. Falls back to a middle initial if the two-part pool runs dry."""
    capacity = len(GIVEN) * len(SURNAME)
    names, seen = [], set()
    use_middle = n > capacity // 4   # keep rejection sampling cheap
    guard = 0
    while len(names) < n:
        guard += 1
        if guard > 200 * n + 10_000:
            raise RuntimeError(f"could not draw {n} unique names (pool capacity {capacity})")
        g, s = rng.choice(GIVEN), rng.choice(SURNAME)
        name = f"{g} {rng.choice(GIVEN)[0]}. {s}" if use_middle else f"{g} {s}"
        if name in seen:
            continue
        seen.add(name)
        names.append(name)
    return names


def _birth_date(rng: random.Random) -> str:
    m = rng.randrange(12)
    day = rng.randint(1, DAYS_IN_MONTH[m])
    year = rng.randint(*YEAR_RANGE)
    return f"{MONTHS[m]} {day}, {year}"


def _one_biography(name: str, attrs: Dict[str, str], rng: random.Random) -> dict:
    """One wording of one person's biography: its own template draw and sentence order."""
    order = ATTRIBUTES[:]
    rng.shuffle(order)
    sentences, used = [], {}
    for attr in order:
        t = rng.choice(TEMPLATES[attr])
        used[attr] = TEMPLATES[attr].index(t)
        sentences.append({"attribute": attr,
                          "template_id": used[attr],
                          "sentence": t.format(n=name, v=attrs[attr])})
    return {
        "sentence_order": order,
        "template_ids": used,
        "sentences": [x["sentence"] for x in sentences],
        "sentence_meta": sentences,
        "text": " ".join(x["sentence"] for x in sentences),
    }


def generate(n: int, seed: int = 0, rewordings: int = 4,
             qa_split: bool = False, qa_test_fraction: float = 0.5) -> Iterator[dict]:
    """Yield n people. The seed fully determines the output.

    rewordings: how many independently worded biographies to emit per person. bioS
        relies on paraphrase: the same fact stated several ways is what forces the
        model to store the fact rather than memorize one surface form.
    qa_split: assign each person to "qa_train" or "qa_test". Training may show the
        QA pairs of the qa_train half only; extraction accuracy is then measured on
        the qa_test half, whose facts the model has seen only inside biographies.
    """
    _check_templates()
    if rewordings < 1:
        raise ValueError("rewordings must be >= 1")
    rng = random.Random(seed)
    names = _unique_names(n, rng)

    # draw the split up front from its own stream, so changing `rewordings` does not
    # move people between halves
    split_rng = random.Random(seed ^ 0x5F5F5F)
    order = list(range(n))
    split_rng.shuffle(order)
    n_test = int(round(n * qa_test_fraction))
    test_ids = set(order[:n_test])

    for i, name in enumerate(names):
        attrs = {
            "birth_date": _birth_date(rng),
            "birth_city": rng.choice(CITIES),
            "university": rng.choice(UNIVERSITIES),
            "major": rng.choice(MAJORS),
            "employer": rng.choice(EMPLOYERS),
        }

        bios = [_one_biography(name, attrs, rng) for _ in range(rewordings)]
        for j, b in enumerate(bios):
            b["rewording_id"] = j

        qa = []
        for attr in ATTRIBUTES:
            q = rng.choice(QUESTIONS[attr])
            qa.append({"attribute": attr,
                       "question": q.format(n=name),
                       "answer": attrs[attr]})

        rec = {
            "id": i,
            "name": name,
            "attributes": attrs,
            "n_rewordings": rewordings,
            "biographies": bios,
            "qa": qa,
            # convenience mirrors of biographies[0], kept so step-0 consumers still work
            "sentence_order": bios[0]["sentence_order"],
            "template_ids": bios[0]["template_ids"],
            "sentences": bios[0]["sentences"],
            "sentence_meta": bios[0]["sentence_meta"],
            "text": bios[0]["text"],
        }
        if qa_split:
            rec["qa_split"] = "qa_test" if i in test_ids else "qa_train"
        yield rec


# the generative space of birth dates, for the record: 366 day-slots x 61 years
_BIRTH_DATE_SPACE = sum(DAYS_IN_MONTH) * (YEAR_RANGE[1] - YEAR_RANGE[0] + 1)

POOLS: Dict[str, Optional[List[str]]] = {
    "birth_city": CITIES,
    "university": UNIVERSITIES,
    "major": MAJORS,
    "employer": EMPLOYERS,
    "birth_date": None,       # combinatorial; the candidate set is what was observed
}


def attribute_values(people: List[dict]) -> dict:
    """The candidate set per attribute, for ranking which answer a model stores.

    For the four categorical attributes this is the full generator pool, which is a
    superset of what any sample contains. birth_date is combinatorial (22,326
    possibilities), so ranking over the whole space is not useful and the candidate
    set is the values actually present in this file.
    """
    out = {}
    for attr in ATTRIBUTES:
        observed = sorted({p["attributes"][attr] for p in people})
        pool = POOLS[attr]
        values = sorted(set(pool) | set(observed)) if pool is not None else observed
        out[attr] = {
            "n_candidates": len(values),
            "n_observed": len(observed),
            "source": "full generator pool (superset of observed)" if pool is not None
                      else "observed in this file (space is combinatorial)",
            "generative_space_size": len(pool) if pool is not None else _BIRTH_DATE_SPACE,
            "values": values,
        }
    return {"attributes": out, "attribute_order": ATTRIBUTES, "n_people": len(people)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="data_samples/bios_sample.jsonl")
    ap.add_argument("--rewordings", type=int, default=4,
                    help="biographies per person, each with its own templates and order")
    ap.add_argument("--qa-split", action="store_true",
                    help="tag each person qa_train / qa_test so extraction can be "
                         "measured on facts whose QA pairs training never saw")
    ap.add_argument("--qa-test-fraction", type=float, default=0.5)
    ap.add_argument("--count-tokens", action="store_true",
                    help="tokenize with the GPT-2 encoding and extrapolate to 10k / 100k people")
    args = ap.parse_args()

    people = list(generate(args.n, args.seed, rewordings=args.rewordings,
                           qa_split=args.qa_split,
                           qa_test_fraction=args.qa_test_fraction))
    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        for p in people:
            f.write(json.dumps(p) + "\n")

    values_path = out_path.with_name("attribute_values.json")
    values_path.write_text(json.dumps(attribute_values(people), indent=2))

    names = {p["name"] for p in people}
    print(f"wrote {len(people)} people to {out_path}")
    print(f"wrote candidate sets to {values_path}")
    print(f"unique names: {len(names)} (duplicates: {len(people) - len(names)})")
    print(f"pool capacity: {len(GIVEN)} given x {len(SURNAME)} surnames = "
          f"{len(GIVEN) * len(SURNAME):,} two-part names")
    print(f"rewordings per person: {args.rewordings} "
          f"({len(people) * args.rewordings:,} biographies total)")
    if args.qa_split:
        from collections import Counter
        c = Counter(p["qa_split"] for p in people)
        print(f"qa split: {dict(c)}")
    av = attribute_values(people)["attributes"]
    print("candidate sets: " + ", ".join(
        f"{a}={v['n_candidates']} (observed {v['n_observed']})" for a, v in av.items()))

    print("\nexample (first person, first two rewordings):")
    ex = dict(people[0])
    ex["biographies"] = ex["biographies"][:2]
    for k in ("sentence_meta", "sentences", "sentence_order", "template_ids"):
        ex.pop(k, None)
    print(json.dumps(ex, indent=2))

    if args.count_tokens:
        import tiktoken
        enc = tiktoken.get_encoding("gpt2")
        bio = sum(len(enc.encode(b["text"])) for p in people for b in p["biographies"])
        qa = sum(len(enc.encode(q["question"] + " " + q["answer"]))
                 for p in people for q in p["qa"])
        n = len(people)
        print(f"\n--- tokens (GPT-2 encoding), measured on {n} people "
              f"x {args.rewordings} rewordings ---")
        print(f"biography text : {bio:,} tok  ({bio / n:.1f} / person)")
        print(f"QA pairs       : {qa:,} tok  ({qa / n:.1f} / person)")
        print(f"total          : {bio + qa:,} tok  ({(bio + qa) / n:.1f} / person)")
        for scale in (10_000, 100_000):
            f = scale / n
            print(f"\n{scale:,} people -> bios {bio * f / 1e6:.2f}M tok, "
                  f"QA {qa * f / 1e6:.2f}M tok, total {(bio + qa) * f / 1e6:.2f}M tok "
                  f"({(bio + qa) * f * 2 / 1e6:.1f} MB as uint16)")


if __name__ == "__main__":
    main()
