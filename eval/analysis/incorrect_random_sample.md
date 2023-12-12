### 1. entry-62
**Question:** What major is every student who does not own a cat as a pet, and also how old are they?

**Difficulty:** extra

**DB Info:** pets_1
```
# student ( stuid , lname , fname , age , sex , major , advisor , city_code )
# has_pet ( stuid , petid )
# pets ( petid , pettype , pet_age , weight )
# has_pet.stuid = student.stuid
# has_pet.petid = pets.petid
```
**SQLChatGPT:**
```sql
SELECT s.major,
       s.age
FROM student s
WHERE s.stuid NOT IN
    (SELECT hp.stuid
     FROM has_pet hp
     JOIN pets p ON hp.petid = p.petid
     WHERE p.pettype = 'Cat' );
```
| major | age |
| --- | --- |
| 600 | 18 |
| 600 | 19 |
| 600 | 21 |
| 600 | 20 |
| 600 | 26 |
| 600 | 18 |
| 600 | 18 |
| 600 | 20 |
| 600 | 19 |
| 600 | 17 |
| 600 | 22 |
| 600 | 20 |
| 600 | 18 |
| 600 | 16 |
| 600 | 17 |
| 600 | 27 |
| 600 | 20 |
| 600 | 18 |
| 520 | 22 |
| 520 | 19 |
| 540 | 17 |
| 520 | 20 |
| 540 | 18 |
| 520 | 18 |
| 520 | 19 |
| 520 | 18 |
| 550 | 20 |
| 100 | 17 |
| 550 | 21 |
| 550 | 20 |
| 550 | 20 |
| 550 | 18 |
| 50 | 18 |
| 50 | 26 |

**GOLD:**
```sql
SELECT major,
       age
FROM student
WHERE stuid NOT IN
    (SELECT student.stuid
     FROM student
     JOIN has_pet ON student.stuid = has_pet.stuid
     JOIN pets ON pets.petid = has_pet.petid
     WHERE pets.pettype = 'cat' )
```

| major | age |
| --- | --- |
| 600 | 19 |
| 600 | 21 |
| 600 | 20 |
| 600 | 26 |
| 600 | 18 |
| 600 | 18 |
| 600 | 20 |
| 600 | 19 |
| 600 | 17 |
| 600 | 22 |
| 600 | 20 |
| 600 | 18 |
| 600 | 16 |
| 600 | 17 |
| 600 | 27 |
| 600 | 20 |
| 600 | 18 |
| 520 | 22 |
| 520 | 19 |
| 540 | 17 |
| 520 | 20 |
| 540 | 18 |
| 520 | 18 |
| 520 | 19 |
| 520 | 18 |
| 550 | 20 |
| 100 | 17 |
| 550 | 21 |
| 550 | 20 |
| 550 | 20 |
| 550 | 18 |
| 50 | 18 |
| 50 | 26 |

### 2. entry-229
**Question:** Which airline has most number of flights?

**Difficulty:** extra

**DB Info:** flight_2
```
# airlines ( uid , airline , abbreviation , country )
# airports ( city , airportcode , airportname , country , countryabbrev )
# flights ( airline , flightno , sourceairport , destairport )
# flights.destairport = airports.airportcode
# flights.sourceairport = airports.airportcode
```
**SQLChatGPT:**
```sql
SELECT airline,
       COUNT(*) AS flight_count
FROM flights
GROUP BY airline
ORDER BY flight_count DESC
LIMIT 1;
```
| airline | flight_count |
| --- | --- |
| 1 | 100 |

**GOLD:**
```sql
SELECT airlines.airline
FROM airlines
JOIN flights ON airlines.uid = flights.airline
GROUP BY airlines.airline
ORDER BY COUNT (*) DESC
LIMIT 1
```

| airline |
| --- |
| Virgin America |

### 3. entry-227
**Question:** What is the code of airport that has fewest number of flights?

**Difficulty:** extra

**DB Info:** flight_2
```
# airlines ( uid , airline , abbreviation , country )
# airports ( city , airportcode , airportname , country , countryabbrev )
# flights ( airline , flightno , sourceairport , destairport )
# flights.destairport = airports.airportcode
# flights.sourceairport = airports.airportcode
```
**SQLChatGPT:**
```sql
SELECT airport
FROM
  (SELECT sourceairport AS airport
   FROM flights
   UNION ALL SELECT destairport AS airport
   FROM flights) AS combined
GROUP BY airport
ORDER BY COUNT(*) ASC
LIMIT 1;
```
| airport |
| --- |
|  AID |

**GOLD:**
```sql
SELECT airports.airportcode
FROM airports
JOIN flights ON airports.airportcode = flights.destairport
OR airports.airportcode = flights.sourceairport
GROUP BY airports.airportcode
ORDER BY COUNT (*) ASC
LIMIT 1
```

| airportcode |
| --- |

### 4. entry-944
**Question:** What are the first name and last name of the professionals who have done treatment with cost below average?

**Difficulty:** extra

**DB Info:** dog_kennels
```
# breeds ( breed_code , breed_name )
# charges ( charge_id , charge_type , charge_amount )
# sizes ( size_code , size_description )
# treatment_types ( treatment_type_code , treatment_type_description )
# owners ( owner_id , first_name , last_name , street , city , state , zip_code , email_address , home_phone , cell_number )
# dogs ( dog_id , owner_id , abandoned_yn , breed_code , size_code , name , age , date_of_birth , gender , weight , date_arrived , date_adopted , date_departed )
# professionals ( professional_id , role_code , first_name , street , city , state , zip_code , last_name , email_address , home_phone , cell_number )
# treatments ( treatment_id , dog_id , professional_id , treatment_type_code , date_of_treatment , cost_of_treatment )
# dogs.owner_id = owners.owner_id
# dogs.owner_id = owners.owner_id
# dogs.size_code = sizes.size_code
# dogs.breed_code = breeds.breed_code
# treatments.dog_id = dogs.dog_id
# treatments.professional_id = professionals.professional_id
# treatments.treatment_type_code = treatment_types.treatment_type_code
```
**SQLChatGPT:**
```sql
SELECT DISTINCT p.first_name,
                p.last_name
FROM professionals p
JOIN treatments t ON p.professional_id = t.professional_id
WHERE t.cost_of_treatment <
    (SELECT AVG(cost_of_treatment)
     FROM treatments);
```
| first_name | last_name |
| --- | --- |
| Domenica | Jacobs |
| Vernice | Tillman |
| Karley | Hyatt |
| Ruben | O'Reilly |
| Monte | Kshlerin |

**GOLD:**
```sql
SELECT DISTINCT professionals.first_name,
                professionals.last_name
FROM professionals
JOIN treatments
WHERE cost_of_treatment <
    (SELECT AVG (cost_of_treatment)
     FROM treatments)
```

| first_name | last_name |
| --- | --- |
| Taryn | Braun |
| Jayson | Ullrich |
| Olaf | Watsica |
| Vernice | Tillman |
| Danny | Considine |
| Ruben | O'Reilly |
| Velva | Hayes |
| Karley | Hyatt |
| Monte | Kshlerin |
| Domenica | Jacobs |
| Brady | Pouros |
| Winfield | Christiansen |
| Ericka | Murazik |
| Sigurd | Frami |
| Lesly | Walter |

### 5. entry-542
**Question:** What is the first, middle, and last name, along with the id and number of enrollments, for the student who enrolled the most in any program?

**Difficulty:** extra

**DB Info:** student_transcripts_tracking
```
# addresses ( address_id , line_1 , line_2 , line_3 , city , zip_postcode , state_province_county , country , other_address_details )
# courses ( course_id , course_name , course_description , other_details )
# departments ( department_id , department_name , department_description , other_details )
# degree_programs ( degree_program_id , department_id , degree_summary_name , degree_summary_description , other_details )
# sections ( section_id , course_id , section_name , section_description , other_details )
# semesters ( semester_id , semester_name , semester_description , other_details )
# students ( student_id , current_address_id , permanent_address_id , first_name , middle_name , last_name , cell_mobile_number , email_address , ssn , date_first_registered , date_left , other_student_details )
# student_enrolment ( student_enrolment_id , degree_program_id , semester_id , student_id , other_details )
# student_enrolment_courses ( student_course_id , course_id , student_enrolment_id )
# transcripts ( transcript_id , transcript_date , other_details )
# transcript_contents ( student_course_id , transcript_id )
# degree_programs.department_id = departments.department_id
# sections.course_id = courses.course_id
# students.permanent_address_id = addresses.address_id
# students.current_address_id = addresses.address_id
# student_enrolment.student_id = students.student_id
# student_enrolment.semester_id = semesters.semester_id
# student_enrolment.degree_program_id = degree_programs.degree_program_id
# student_enrolment_courses.student_enrolment_id = student_enrolment.student_enrolment_id
# student_enrolment_courses.course_id = courses.course_id
# transcript_contents.transcript_id = transcripts.transcript_id
# transcript_contents.student_course_id = student_enrolment_courses.student_course_id
```
**SQLChatGPT:**
```sql
SELECT s.first_name,
       s.middle_name,
       s.last_name,
       s.student_id,
       COUNT(*) AS total_enrollments
FROM students s
JOIN student_enrolment se ON s.student_id = se.student_id
GROUP BY s.student_id,
         s.first_name,
         s.middle_name,
         s.last_name
ORDER BY total_enrollments DESC
LIMIT 1;
```
| first_name | middle_name | last_name | student_id | total_enrollments |
| --- | --- | --- | --- | --- |
| Stanford | Mona | Rogahn | 6 | 3 |

**GOLD:**
```sql
SELECT students.student_id,
       students.first_name,
       students.middle_name,
       students.last_name,
       COUNT (*) , students.student_id
FROM students
JOIN student_enrolment ON students.student_id = student_enrolment.student_id
GROUP BY students.student_id
ORDER BY COUNT (*) DESC
LIMIT 1
```

| student_id | first_name | middle_name | last_name | count (*) | student_id |
| --- | --- | --- | --- | --- | --- |
| 7 | Frida | Aisha | Huel | 3 | 7 |

### 6. entry-131
**Question:** What is the maximum horsepower and the make of the car models with 3 cylinders?

**Difficulty:** extra

**DB Info:** car_1
```
# continents ( contid , continent )
# countries ( countryid , countryname , continent )
# car_makers ( id , maker , fullname , country )
# model_list ( modelid , maker , model )
# car_names ( makeid , model , make )
# cars_data ( id , mpg , cylinders , edispl , horsepower , weight , accelerate , year )
# countries.continent = continents.contid
# car_makers.country = countries.countryid
# model_list.maker = car_makers.id
# car_names.model = model_list.model
# cars_data.id = car_names.makeid
```
**SQLChatGPT:**
```sql
SELECT MAX(cars_data.horsepower) AS max_horsepower,
       car_names.make
FROM cars_data
INNER JOIN car_names ON cars_data.id = car_names.makeid
WHERE cars_data.cylinders = 3
GROUP BY car_names.make;
```
| max_horsepower | make |
| --- | --- |
| 110 | mazda rx-4 |
| 100 | mazda rx-7 gs |
| 97 | mazda rx2 coupe |
| 90 | mazda rx3 |

**GOLD:**
```sql
SELECT cars_data.horsepower,
       car_names.make
FROM car_names
JOIN cars_data ON car_names.makeid = cars_data.id
WHERE cars_data.cylinders = 3
ORDER BY cars_data.horsepower DESC
LIMIT 1
```

| horsepower | make |
| --- | --- |
| 97 | mazda rx2 coupe |

### 7. entry-755
**Question:** Which countries have either English or Dutch as an official language?

**Difficulty:** extra

**DB Info:** world_1
```
# city ( id , name , countrycode , district , population )
# sqlite_sequence ( name , seq )
# country ( code , name , continent , region , surfacearea , indepyear , population , lifeexpectancy , gnp , gnpold , localname , governmentform , headofstate , capital , code2 )
# countrylanguage ( countrycode , language , isofficial , percentage )
# city.countrycode = country.code
# countrylanguage.countrycode = country.code
```
**SQLChatGPT:**
```sql
SELECT DISTINCT c.name
FROM country c
JOIN countrylanguage cl ON c.code = cl.countrycode
WHERE (cl.language = 'English'
       OR cl.language = 'Dutch')
  AND cl.isofficial = 'T';
```
| name |
| --- |
| Aruba |
| Anguilla |
| Netherlands Antilles |
| American Samoa |
| Antigua and Barbuda |
| Australia |
| Belgium |
| Belize |
| Bermuda |
| Barbados |
| Canada |
| Cocos (Keeling) Islands |
| Christmas Island |
| Cayman Islands |
| Falkland Islands |
| United Kingdom |
| Gibraltar |
| Guam |
| Hong Kong |
| Ireland |
| Saint Kitts and Nevis |
| Saint Lucia |
| Lesotho |
| Marshall Islands |
| Malta |
| Northern Mariana Islands |
| Montserrat |
| Norfolk Island |
| Niue |
| Netherlands |
| Nauru |
| New Zealand |
| Palau |
| Saint Helena |
| Seychelles |
| Turks and Caicos Islands |
| Tokelau |
| Tonga |
| Tuvalu |
| United States Minor Outlying Islands |
| United States |
| Saint Vincent and the Grenadines |
| Virgin Islands, British |
| Virgin Islands, U.S. |
| Vanuatu |
| Samoa |
| South Africa |
| Zimbabwe |

**GOLD:**
```sql
SELECT *
FROM country
JOIN countrylanguage ON country.code = countrylanguage.countrycode
WHERE countrylanguage.language = 'English'
  AND isofficial = 'T'
UNION
SELECT *
FROM country
JOIN countrylanguage ON country.code = countrylanguage.countrycode
WHERE countrylanguage.language = 'Dutch'
  AND isofficial = 'T'
```

| code | name | continent | region | surfacearea | indepyear | population | lifeexpectancy | gnp | gnpold | localname | governmentform | headofstate | capital | code2 | countrycode | language | isofficial | percentage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ABW | Aruba | North America | Caribbean | 193.0 | None | 103000 | 78.4 | 828.0 | 793.0 | Aruba | Nonmetropolitan Territory of The Netherlands | Beatrix | 129 | AW | ABW | Dutch | T | 5.3 |
| AIA | Anguilla | North America | Caribbean | 96.0 | None | 8000 | 76.1 | 63.2 | None | Anguilla | Dependent Territory of the UK | Elisabeth II | 62 | AI | AIA | English | T | 0.0 |
| ANT | Netherlands Antilles | North America | Caribbean | 800.0 | None | 217000 | 74.7 | 1941.0 | None | Nederlandse Antillen | Nonmetropolitan Territory of The Netherlands | Beatrix | 33 | AN | ANT | Dutch | T | 0.0 |
| ASM | American Samoa | Oceania | Polynesia | 199.0 | None | 68000 | 75.1 | 334.0 | None | Amerika Samoa | US Territory | George W. Bush | 54 | AS | ASM | English | T | 3.1 |
| ATG | Antigua and Barbuda | North America | Caribbean | 442.0 | 1981 | 68000 | 70.5 | 612.0 | 584.0 | Antigua and Barbuda | Constitutional Monarchy | Elisabeth II | 63 | AG | ATG | English | T | 0.0 |
| AUS | Australia | Oceania | Australia and New Zealand | 7741220.0 | 1901 | 18886000 | 79.8 | 351182.0 | 392911.0 | Australia | Constitutional Monarchy, Federation | Elisabeth II | 135 | AU | AUS | English | T | 81.2 |
| BEL | Belgium | Europe | Western Europe | 30518.0 | 1830 | 10239000 | 77.8 | 249704.0 | 243948.0 | België/Belgique | Constitutional Monarchy, Federation | Albert II | 179 | BE | BEL | Dutch | T | 59.2 |
| BLZ | Belize | North America | Central America | 22696.0 | 1981 | 241000 | 70.9 | 630.0 | 616.0 | Belize | Constitutional Monarchy | Elisabeth II | 185 | BZ | BLZ | English | T | 50.8 |
| BMU | Bermuda | North America | North America | 53.0 | None | 65000 | 76.9 | 2328.0 | 2190.0 | Bermuda | Dependent Territory of the UK | Elisabeth II | 191 | BM | BMU | English | T | 100.0 |
| BRB | Barbados | North America | Caribbean | 430.0 | 1966 | 270000 | 73.0 | 2223.0 | 2186.0 | Barbados | Constitutional Monarchy | Elisabeth II | 174 | BB | BRB | English | T | 0.0 |
| CAN | Canada | North America | North America | 9970610.0 | 1867 | 31147000 | 79.4 | 598862.0 | 625626.0 | Canada | Constitutional Monarchy, Federation | Elisabeth II | 1822 | CA | CAN | English | T | 60.4 |
| CCK | Cocos (Keeling) Islands | Oceania | Australia and New Zealand | 14.0 | None | 600 | None | 0.0 | None | Cocos (Keeling) Islands | Territory of Australia | Elisabeth II | 2317 | CC | CCK | English | T | 0.0 |
| CXR | Christmas Island | Oceania | Australia and New Zealand | 135.0 | None | 2500 | None | 0.0 | None | Christmas Island | Territory of Australia | Elisabeth II | 1791 | CX | CXR | English | T | 0.0 |
| CYM | Cayman Islands | North America | Caribbean | 264.0 | None | 38000 | 78.9 | 1263.0 | 1186.0 | Cayman Islands | Dependent Territory of the UK | Elisabeth II | 553 | KY | CYM | English | T | 0.0 |
| FLK | Falkland Islands | South America | South America | 12173.0 | None | 2000 | None | 0.0 | None | Falkland Islands | Dependent Territory of the UK | Elisabeth II | 763 | FK | FLK | English | T | 0.0 |
| GBR | United Kingdom | Europe | British Islands | 242900.0 | 1066 | 59623400 | 77.7 | 1378330.0 | 1296830.0 | United Kingdom | Constitutional Monarchy | Elisabeth II | 456 | GB | GBR | English | T | 97.3 |
| GIB | Gibraltar | Europe | Southern Europe | 6.0 | None | 25000 | 79.0 | 258.0 | None | Gibraltar | Dependent Territory of the UK | Elisabeth II | 915 | GI | GIB | English | T | 88.9 |
| GUM | Guam | Oceania | Micronesia | 549.0 | None | 168000 | 77.8 | 1197.0 | 1136.0 | Guam | US Territory | George W. Bush | 921 | GU | GUM | English | T | 37.5 |
| HKG | Hong Kong | Asia | Eastern Asia | 1075.0 | None | 6782000 | 79.5 | 166448.0 | 173610.0 | Xianggang/Hong Kong | Special Administrative Region of China | Jiang Zemin | 937 | HK | HKG | English | T | 2.2 |
| IRL | Ireland | Europe | British Islands | 70273.0 | 1921 | 3775100 | 76.8 | 75921.0 | 73132.0 | Ireland/Éire | Republic | Mary McAleese | 1447 | IE | IRL | English | T | 98.4 |
| KNA | Saint Kitts and Nevis | North America | Caribbean | 261.0 | 1983 | 38000 | 70.7 | 299.0 | None | Saint Kitts and Nevis | Constitutional Monarchy | Elisabeth II | 3064 | KN | KNA | English | T | 0.0 |
| LCA | Saint Lucia | North America | Caribbean | 622.0 | 1979 | 154000 | 72.3 | 571.0 | None | Saint Lucia | Constitutional Monarchy | Elisabeth II | 3065 | LC | LCA | English | T | 20.0 |
| LSO | Lesotho | Africa | Southern Africa | 30355.0 | 1966 | 2153000 | 50.8 | 1061.0 | 1161.0 | Lesotho | Constitutional Monarchy | Letsie III | 2437 | LS | LSO | English | T | 0.0 |
| MHL | Marshall Islands | Oceania | Micronesia | 181.0 | 1990 | 64000 | 65.5 | 97.0 | None | Marshall Islands/Majol | Republic | Kessai Note | 2507 | MH | MHL | English | T | 0.0 |
| MLT | Malta | Europe | Southern Europe | 316.0 | 1964 | 380200 | 77.9 | 3512.0 | 3338.0 | Malta | Republic | Guido de Marco | 2484 | MT | MLT | English | T | 2.1 |
| MNP | Northern Mariana Islands | Oceania | Micronesia | 464.0 | None | 78000 | 75.5 | 0.0 | None | Northern Mariana Islands | Commonwealth of the US | George W. Bush | 2913 | MP | MNP | English | T | 4.8 |
| MSR | Montserrat | North America | Caribbean | 102.0 | None | 11000 | 78.0 | 109.0 | None | Montserrat | Dependent Territory of the UK | Elisabeth II | 2697 | MS | MSR | English | T | 0.0 |
| NFK | Norfolk Island | Oceania | Australia and New Zealand | 36.0 | None | 2000 | None | 0.0 | None | Norfolk Island | Territory of Australia | Elisabeth II | 2806 | NF | NFK | English | T | 0.0 |
| NIU | Niue | Oceania | Polynesia | 260.0 | None | 2000 | None | 0.0 | None | Niue | Nonmetropolitan Territory of New Zealand | Elisabeth II | 2805 | NU | NIU | English | T | 0.0 |
| NLD | Netherlands | Europe | Western Europe | 41526.0 | 1581 | 15864000 | 78.3 | 371362.0 | 360478.0 | Nederland | Constitutional Monarchy | Beatrix | 5 | NL | NLD | Dutch | T | 95.6 |
| NRU | Nauru | Oceania | Micronesia | 21.0 | 1968 | 12000 | 60.8 | 197.0 | None | Naoero/Nauru | Republic | Bernard Dowiyogo | 2728 | NR | NRU | English | T | 7.5 |
| NZL | New Zealand | Oceania | Australia and New Zealand | 270534.0 | 1907 | 3862000 | 77.8 | 54669.0 | 64960.0 | New Zealand/Aotearoa | Constitutional Monarchy | Elisabeth II | 3499 | NZ | NZL | English | T | 87.0 |
| PLW | Palau | Oceania | Micronesia | 459.0 | 1994 | 19000 | 68.6 | 105.0 | None | Belau/Palau | Republic | Kuniwo Nakamura | 2881 | PW | PLW | English | T | 3.2 |
| SHN | Saint Helena | Africa | Western Africa | 314.0 | None | 6000 | 76.8 | 0.0 | None | Saint Helena | Dependent Territory of the UK | Elisabeth II | 3063 | SH | SHN | English | T | 0.0 |
| SYC | Seychelles | Africa | Eastern Africa | 455.0 | 1976 | 77000 | 70.4 | 536.0 | 539.0 | Sesel/Seychelles | Republic | France-Albert René | 3206 | SC | SYC | English | T | 3.8 |
| TCA | Turks and Caicos Islands | North America | Caribbean | 430.0 | None | 17000 | 73.3 | 96.0 | None | The Turks and Caicos Islands | Dependent Territory of the UK | Elisabeth II | 3423 | TC | TCA | English | T | 0.0 |
| TKL | Tokelau | Oceania | Polynesia | 12.0 | None | 2000 | None | 0.0 | None | Tokelau | Nonmetropolitan Territory of New Zealand | Elisabeth II | 3333 | TK | TKL | English | T | 0.0 |
| TON | Tonga | Oceania | Polynesia | 650.0 | 1970 | 99000 | 67.9 | 146.0 | 170.0 | Tonga | Monarchy | Taufa'ahau Tupou IV | 3334 | TO | TON | English | T | 0.0 |
| TUV | Tuvalu | Oceania | Polynesia | 26.0 | 1978 | 12000 | 66.3 | 6.0 | None | Tuvalu | Constitutional Monarchy | Elisabeth II | 3424 | TV | TUV | English | T | 0.0 |
| UMI | United States Minor Outlying Islands | Oceania | Micronesia/Caribbean | 16.0 | None | 0 | None | 0.0 | None | United States Minor Outlying Islands | Dependent Territory of the US | George W. Bush | None | UM | UMI | English | T | 0.0 |
| USA | United States | North America | North America | 9363520.0 | 1776 | 278357000 | 77.1 | 8510700.0 | 8110900.0 | United States | Federal Republic | George W. Bush | 3813 | US | USA | English | T | 86.2 |
| VCT | Saint Vincent and the Grenadines | North America | Caribbean | 388.0 | 1979 | 114000 | 72.3 | 285.0 | None | Saint Vincent and the Grenadines | Constitutional Monarchy | Elisabeth II | 3066 | VC | VCT | English | T | 0.0 |
| VGB | Virgin Islands, British | North America | Caribbean | 151.0 | None | 21000 | 75.4 | 612.0 | 573.0 | British Virgin Islands | Dependent Territory of the UK | Elisabeth II | 537 | VG | VGB | English | T | 0.0 |
| VIR | Virgin Islands, U.S. | North America | Caribbean | 347.0 | None | 93000 | 78.1 | 0.0 | None | Virgin Islands of the United States | US Territory | George W. Bush | 4067 | VI | VIR | English | T | 81.7 |
| VUT | Vanuatu | Oceania | Melanesia | 12189.0 | 1980 | 190000 | 60.6 | 261.0 | 246.0 | Vanuatu | Republic | John Bani | 3537 | VU | VUT | English | T | 28.3 |
| WSM | Samoa | Oceania | Polynesia | 2831.0 | 1962 | 180000 | 69.2 | 141.0 | 157.0 | Samoa | Parlementary Monarchy | Malietoa Tanumafili II | 3169 | WS | WSM | English | T | 0.6 |
| ZAF | South Africa | Africa | Southern Africa | 1221037.0 | 1910 | 40377000 | 51.1 | 116729.0 | 129092.0 | South Africa | Republic | Thabo Mbeki | 716 | ZA | ZAF | English | T | 8.5 |
| ZWE | Zimbabwe | Africa | Eastern Africa | 390757.0 | 1980 | 11669000 | 37.8 | 5951.0 | 8670.0 | Zimbabwe | Republic | Robert G. Mugabe | 4068 | ZW | ZWE | English | T | 2.2 |

### 8. entry-541
**Question:** Which student has enrolled for the most times in any program? List the id, first name, middle name, last name, the number of enrollments and student id.

**Difficulty:** extra

**DB Info:** student_transcripts_tracking
```
# addresses ( address_id , line_1 , line_2 , line_3 , city , zip_postcode , state_province_county , country , other_address_details )
# courses ( course_id , course_name , course_description , other_details )
# departments ( department_id , department_name , department_description , other_details )
# degree_programs ( degree_program_id , department_id , degree_summary_name , degree_summary_description , other_details )
# sections ( section_id , course_id , section_name , section_description , other_details )
# semesters ( semester_id , semester_name , semester_description , other_details )
# students ( student_id , current_address_id , permanent_address_id , first_name , middle_name , last_name , cell_mobile_number , email_address , ssn , date_first_registered , date_left , other_student_details )
# student_enrolment ( student_enrolment_id , degree_program_id , semester_id , student_id , other_details )
# student_enrolment_courses ( student_course_id , course_id , student_enrolment_id )
# transcripts ( transcript_id , transcript_date , other_details )
# transcript_contents ( student_course_id , transcript_id )
# degree_programs.department_id = departments.department_id
# sections.course_id = courses.course_id
# students.permanent_address_id = addresses.address_id
# students.current_address_id = addresses.address_id
# student_enrolment.student_id = students.student_id
# student_enrolment.semester_id = semesters.semester_id
# student_enrolment.degree_program_id = degree_programs.degree_program_id
# student_enrolment_courses.student_enrolment_id = student_enrolment.student_enrolment_id
# student_enrolment_courses.course_id = courses.course_id
# transcript_contents.transcript_id = transcripts.transcript_id
# transcript_contents.student_course_id = student_enrolment_courses.student_course_id
```
**SQLChatGPT:**
```sql
SELECT students.student_id,
       students.first_name,
       students.middle_name,
       students.last_name,
       COUNT(student_enrolment.student_id) AS number_of_enrollments
FROM students
JOIN student_enrolment ON students.student_id = student_enrolment.student_id
GROUP BY students.student_id,
         students.first_name,
         students.middle_name,
         students.last_name
ORDER BY number_of_enrollments DESC
LIMIT 1;
```
| student_id | first_name | middle_name | last_name | number_of_enrollments |
| --- | --- | --- | --- | --- |
| 6 | Stanford | Mona | Rogahn | 3 |

**GOLD:**
```sql
SELECT students.student_id,
       students.first_name,
       students.middle_name,
       students.last_name,
       COUNT (*) , students.student_id
FROM students
JOIN student_enrolment ON students.student_id = student_enrolment.student_id
GROUP BY students.student_id
ORDER BY COUNT (*) DESC
LIMIT 1
```

| student_id | first_name | middle_name | last_name | count (*) | student_id |
| --- | --- | --- | --- | --- | --- |
| 7 | Frida | Aisha | Huel | 3 | 7 |

### 9. entry-818
**Question:** What is the total number of countries where Spanish is spoken by the largest percentage of people?

**Difficulty:** extra

**DB Info:** world_1
```
# city ( id , name , countrycode , district , population )
# sqlite_sequence ( name , seq )
# country ( code , name , continent , region , surfacearea , indepyear , population , lifeexpectancy , gnp , gnpold , localname , governmentform , headofstate , capital , code2 )
# countrylanguage ( countrycode , language , isofficial , percentage )
# city.countrycode = country.code
# countrylanguage.countrycode = country.code
```
**SQLChatGPT:**
```sql
SELECT COUNT(*)
FROM
  (SELECT cl.countrycode
   FROM countrylanguage cl
   INNER JOIN
     (SELECT countrycode,
             MAX(percentage) AS max_percentage
      FROM countrylanguage
      GROUP BY countrycode) AS max_lang ON cl.countrycode = max_lang.countrycode
   WHERE cl.language = 'Spanish'
     AND cl.percentage = max_lang.max_percentage ) AS spanish_speaking_countries;
```
| count(*) |
| --- |
| 21 |

**GOLD:**
```sql
SELECT COUNT (*) , MAX (percentage)
FROM countrylanguage
WHERE LANGUAGE = 'Spanish'
GROUP BY countrycode
```

| count (*) | max (percentage) |
| --- | --- |
| 1 | 7.4 |
| 1 | 44.6 |
| 1 | 96.8 |
| 1 | 31.6 |
| 1 | 87.7 |
| 1 | 0.7 |
| 1 | 89.7 |
| 1 | 99.0 |
| 1 | 97.5 |
| 1 | 100.0 |
| 1 | 98.0 |
| 1 | 93.0 |
| 1 | 74.4 |
| 1 | 0.4 |
| 1 | 64.7 |
| 1 | 97.2 |
| 1 | 92.1 |
| 1 | 97.6 |
| 1 | 76.8 |
| 1 | 79.8 |
| 1 | 51.3 |
| 1 | 55.1 |
| 1 | 100.0 |
| 1 | 0.6 |
| 1 | 95.7 |
| 1 | 7.5 |
| 1 | 96.9 |
| 1 | 13.3 |

### 10. entry-774
**Question:** What are the African countries that have a  population less than any country in Asia?

**Difficulty:** extra

**DB Info:** world_1
```
# city ( id , name , countrycode , district , population )
# sqlite_sequence ( name , seq )
# country ( code , name , continent , region , surfacearea , indepyear , population , lifeexpectancy , gnp , gnpold , localname , governmentform , headofstate , capital , code2 )
# countrylanguage ( countrycode , language , isofficial , percentage )
# city.countrycode = country.code
# countrylanguage.countrycode = country.code
```
**SQLChatGPT:**
```sql
SELECT name
FROM country
WHERE population <
    (SELECT MIN(population)
     FROM country
     WHERE continent = 'Asia' )
  AND continent = 'Africa';
```
| name |
| --- |
| British Indian Ocean Territory |
| Mayotte |
| Saint Helena |
| Sao Tome and Principe |
| Seychelles |

**GOLD:**
```sql
SELECT name
FROM country
WHERE continent = 'Africa'
  AND population <
    (SELECT MAX (population)
     FROM country
     WHERE continent = 'Asia' )
```

| name |
| --- |
| Angola |
| Burundi |
| Benin |
| Burkina Faso |
| Botswana |
| Central African Republic |
| Côte d’Ivoire |
| Cameroon |
| Congo, The Democratic Republic of the |
| Congo |
| Comoros |
| Cape Verde |
| Djibouti |
| Algeria |
| Egypt |
| Eritrea |
| Western Sahara |
| Ethiopia |
| Gabon |
| Ghana |
| Guinea |
| Gambia |
| Guinea-Bissau |
| Equatorial Guinea |
| British Indian Ocean Territory |
| Kenya |
| Liberia |
| Libyan Arab Jamahiriya |
| Lesotho |
| Morocco |
| Madagascar |
| Mali |
| Mozambique |
| Mauritania |
| Mauritius |
| Malawi |
| Mayotte |
| Namibia |
| Niger |
| Nigeria |
| Réunion |
| Rwanda |
| Sudan |
| Senegal |
| Saint Helena |
| Sierra Leone |
| Somalia |
| Sao Tome and Principe |
| Swaziland |
| Seychelles |
| Chad |
| Togo |
| Tunisia |
| Tanzania |
| Uganda |
| South Africa |
| Zambia |
| Zimbabwe |

### 11. entry-777
**Question:** What are the Asian countries which have a population larger than that of any country in Africa?

**Difficulty:** extra

**DB Info:** world_1
```
# city ( id , name , countrycode , district , population )
# sqlite_sequence ( name , seq )
# country ( code , name , continent , region , surfacearea , indepyear , population , lifeexpectancy , gnp , gnpold , localname , governmentform , headofstate , capital , code2 )
# countrylanguage ( countrycode , language , isofficial , percentage )
# city.countrycode = country.code
# countrylanguage.countrycode = country.code
```
**SQLChatGPT:**
```sql
SELECT a.name
FROM country AS a
WHERE a.continent = 'Asia'
  AND a.population > ALL
    (SELECT b.population
     FROM country AS b
     WHERE b.continent = 'Africa');
```
No results

**GOLD:**
```sql
SELECT name
FROM country
WHERE continent = 'Asia'
  AND population >
    (SELECT MIN (population)
     FROM country
     WHERE continent = 'Africa' )
```

| name |
| --- |
| Afghanistan |
| United Arab Emirates |
| Armenia |
| Azerbaijan |
| Bangladesh |
| Bahrain |
| Brunei |
| Bhutan |
| China |
| Cyprus |
| Georgia |
| Hong Kong |
| Indonesia |
| India |
| Iran |
| Iraq |
| Israel |
| Jordan |
| Japan |
| Kazakstan |
| Kyrgyzstan |
| Cambodia |
| South Korea |
| Kuwait |
| Laos |
| Lebanon |
| Sri Lanka |
| Macao |
| Maldives |
| Myanmar |
| Mongolia |
| Malaysia |
| Nepal |
| Oman |
| Pakistan |
| Philippines |
| North Korea |
| Palestine |
| Qatar |
| Saudi Arabia |
| Singapore |
| Syria |
| Thailand |
| Tajikistan |
| Turkmenistan |
| East Timor |
| Turkey |
| Taiwan |
| Uzbekistan |
| Vietnam |
| Yemen |

### 12. entry-746
**Question:** What are the names of nations speak both English and French?

**Difficulty:** extra

**DB Info:** world_1
```
# city ( id , name , countrycode , district , population )
# sqlite_sequence ( name , seq )
# country ( code , name , continent , region , surfacearea , indepyear , population , lifeexpectancy , gnp , gnpold , localname , governmentform , headofstate , capital , code2 )
# countrylanguage ( countrycode , language , isofficial , percentage )
# city.countrycode = country.code
# countrylanguage.countrycode = country.code
```
**SQLChatGPT:**
```sql
SELECT country.name
FROM country
JOIN countrylanguage AS cl1 ON country.code = cl1.countrycode
WHERE cl1.language = 'English'
  AND cl1.isofficial = 'T' INTERSECT
  SELECT country.name
  FROM country
  JOIN countrylanguage AS cl2 ON country.code = cl2.countrycode WHERE cl2.language = 'French'
  AND cl2.isofficial = 'T';
```
| name |
| --- |
| Canada |
| Seychelles |
| Vanuatu |

**GOLD:**
```sql
SELECT country.name
FROM country
JOIN countrylanguage ON country.code = countrylanguage.countrycode
WHERE countrylanguage.language = 'English' INTERSECT
  SELECT country.name
  FROM country
  JOIN countrylanguage ON country.code = countrylanguage.countrycode WHERE countrylanguage.language = 'French'
```

| name |
| --- |
| Canada |
| Monaco |
| Seychelles |
| United States |
| Vanuatu |
| Virgin Islands, U.S. |

### 13. entry-713
**Question:** What language is predominantly spoken in Aruba?

**Difficulty:** extra

**DB Info:** world_1
```
# city ( id , name , countrycode , district , population )
# sqlite_sequence ( name , seq )
# country ( code , name , continent , region , surfacearea , indepyear , population , lifeexpectancy , gnp , gnpold , localname , governmentform , headofstate , capital , code2 )
# countrylanguage ( countrycode , language , isofficial , percentage )
# city.countrycode = country.code
# countrylanguage.countrycode = country.code
```
**SQLChatGPT:**
```sql
SELECT LANGUAGE
FROM countrylanguage
WHERE countrycode =
    (SELECT code
     FROM country
     WHERE name = 'Aruba')
  AND isofficial = 'T'
ORDER BY percentage DESC
LIMIT 1;
```
| language |
| --- |
| Dutch |

**GOLD:**
```sql
SELECT countrylanguage.language
FROM country
JOIN countrylanguage ON country.code = countrylanguage.countrycode
WHERE country.name = 'Aruba'
ORDER BY percentage DESC
LIMIT 1
```

| language |
| --- |
| Papiamento |

### 14. entry-960
**Question:** List the last name of the owner owning the youngest dog.

**Difficulty:** extra

**DB Info:** dog_kennels
```
# breeds ( breed_code , breed_name )
# charges ( charge_id , charge_type , charge_amount )
# sizes ( size_code , size_description )
# treatment_types ( treatment_type_code , treatment_type_description )
# owners ( owner_id , first_name , last_name , street , city , state , zip_code , email_address , home_phone , cell_number )
# dogs ( dog_id , owner_id , abandoned_yn , breed_code , size_code , name , age , date_of_birth , gender , weight , date_arrived , date_adopted , date_departed )
# professionals ( professional_id , role_code , first_name , street , city , state , zip_code , last_name , email_address , home_phone , cell_number )
# treatments ( treatment_id , dog_id , professional_id , treatment_type_code , date_of_treatment , cost_of_treatment )
# dogs.owner_id = owners.owner_id
# dogs.owner_id = owners.owner_id
# dogs.size_code = sizes.size_code
# dogs.breed_code = breeds.breed_code
# treatments.dog_id = dogs.dog_id
# treatments.professional_id = professionals.professional_id
# treatments.treatment_type_code = treatment_types.treatment_type_code
```
**SQLChatGPT:**
```sql
SELECT o.last_name
FROM owners o
JOIN dogs d ON o.owner_id = d.owner_id
WHERE d.date_of_birth =
    (SELECT MAX(date_of_birth)
     FROM dogs);
```
| last_name |
| --- |
| Mertz |

**GOLD:**
```sql
SELECT owners.last_name
FROM owners
JOIN dogs ON owners.owner_id = dogs.owner_id
WHERE dogs.age =
    (SELECT MAX (age)
     FROM dogs)
```

| last_name |
| --- |
| Feil |
| Fisher |
| Rippin |

### 15. entry-152
**Question:** What are the different models created by either the car maker General Motors or weighed more than 3500?

**Difficulty:** extra

**DB Info:** car_1
```
# continents ( contid , continent )
# countries ( countryid , countryname , continent )
# car_makers ( id , maker , fullname , country )
# model_list ( modelid , maker , model )
# car_names ( makeid , model , make )
# cars_data ( id , mpg , cylinders , edispl , horsepower , weight , accelerate , year )
# countries.continent = continents.contid
# car_makers.country = countries.countryid
# model_list.maker = car_makers.id
# car_names.model = model_list.model
# cars_data.id = car_names.makeid
```
**SQLChatGPT:**
```sql
SELECT DISTINCT ml.model
FROM model_list AS ml
JOIN car_makers AS cm ON ml.maker = cm.id
WHERE cm.fullname = 'General Motors'
UNION
SELECT DISTINCT ml.model
FROM cars_data AS cd
JOIN car_names AS cn ON cd.id = cn.makeid
JOIN model_list AS ml ON cn.model = ml.model
WHERE cd.weight > 3500;
```
| model |
| --- |
| amc |
| buick |
| cadillac |
| chevrolet |
| chrysler |
| dodge |
| ford |
| hi |
| mercedes |
| mercedes-benz |
| mercury |
| oldsmobile |
| plymouth |
| pontiac |

**GOLD:**
```sql
SELECT DISTINCT model_list.model
FROM car_names
JOIN model_list ON car_names.model = model_list.model
JOIN car_makers ON model_list.maker = car_makers.id
JOIN cars_data ON car_names.makeid = cars_data.id
WHERE car_makers.fullname = 'General Motors'
  OR cars_data.weight > 3500
```

| model |
| --- |
| chevrolet |
| buick |
| ford |
| plymouth |
| pontiac |
| amc |
| dodge |
| mercury |
| oldsmobile |
| chrysler |
| mercedes-benz |
| cadillac |
| mercedes |

### 16. entry-890
**Question:** Show the names of all of the high schooler Kyle's friends.

**Difficulty:** hard

**DB Info:** network_1
```
# highschooler ( id , name , grade )
# friend ( student_id , friend_id )
# likes ( student_id , liked_id )
# friend.friend_id = highschooler.id
# friend.student_id = highschooler.id
# likes.student_id = highschooler.id
# likes.liked_id = highschooler.id
```
**SQLChatGPT:**
```sql
SELECT h2.name
FROM friend
JOIN highschooler h1 ON friend.student_id = h1.id
JOIN highschooler h2 ON friend.friend_id = h2.id
WHERE h1.name = 'Kyle';
```
| name |
| --- |
| Jordan |

**GOLD:**
```sql
SELECT highschooler.name
FROM friend
JOIN highschooler ON friend.student_id = highschooler.id
JOIN highschooler ON friend.friend_id = highschooler.id
WHERE highschooler.name = 'Kyle'
```

No results

### 17. entry-645
**Question:** find the package option of the tv channel that do not have any cartoon directed by Ben Jones.

**Difficulty:** hard

**DB Info:** tvshow
```
# tv_channel ( id , series_name , country , language , content , pixel_aspect_ratio_par , hight_definition_tv , pay_per_view_ppv , package_option )
# tv_series ( id , episode , air_date , rating , share , 18_49_rating_share , viewers_m , weekly_rank , channel )
# cartoon ( id , title , directed_by , written_by , original_air_date , production_code , channel )
# tv_series.channel = tv_channel.id
# cartoon.channel = tv_channel.id
```
**SQLChatGPT:**
```sql
SELECT DISTINCT tv_channel.package_option
FROM tv_channel
WHERE NOT EXISTS
    (SELECT 1
     FROM cartoon
     WHERE cartoon.directed_by = 'Ben Jones'
       AND cartoon.channel = tv_channel.id );
```
| package_option |
| --- |
| Sky Famiglia |
| no ( FTV ) |
| Sky Famiglia + Sky HD |

**GOLD:**
```sql
SELECT package_option
FROM tv_channel
WHERE id NOT IN
    (SELECT channel
     FROM cartoon
     WHERE directed_by = 'Ben Jones' )
```

| package_option |
| --- |
| Sky Famiglia |
| Sky Famiglia |
| Sky Famiglia |
| Sky Famiglia |
| no ( FTV ) |
| Sky Famiglia + Sky HD |
| no ( FTV ) |
| Sky Famiglia |
| Sky Famiglia |
| Sky Famiglia |
| Sky Famiglia |

### 18. entry-54
**Question:** How many dog pets are raised by female students?

**Difficulty:** hard

**DB Info:** pets_1
```
# student ( stuid , lname , fname , age , sex , major , advisor , city_code )
# has_pet ( stuid , petid )
# pets ( petid , pettype , pet_age , weight )
# has_pet.stuid = student.stuid
# has_pet.petid = pets.petid
```
**SQLChatGPT:**
```sql
SELECT COUNT(*)
FROM has_pet
JOIN pets ON has_pet.petid = pets.petid
JOIN student ON student.stuid = has_pet.stuid
WHERE student.sex = 'Female'
  AND pets.pettype = 'dog';
```
| count(*) |
| --- |
| 0 |

**GOLD:**
```sql
SELECT COUNT (*)
FROM student
JOIN has_pet ON student.stuid = has_pet.stuid
JOIN pets ON has_pet.petid = pets.petid
WHERE student.sex = 'F'
  AND pets.pettype = 'dog'
```

| count (*) |
| --- |
| 2 |

### 19. entry-786
**Question:** Which unique cities are in Asian countries where Chinese is the official language ?

**Difficulty:** hard

**DB Info:** world_1
```
# city ( id , name , countrycode , district , population )
# sqlite_sequence ( name , seq )
# country ( code , name , continent , region , surfacearea , indepyear , population , lifeexpectancy , gnp , gnpold , localname , governmentform , headofstate , capital , code2 )
# countrylanguage ( countrycode , language , isofficial , percentage )
# city.countrycode = country.code
# countrylanguage.countrycode = country.code
```
**SQLChatGPT:**
```sql
SELECT DISTINCT city.name
FROM city
JOIN country ON city.countrycode = country.code
JOIN countrylanguage ON countrylanguage.countrycode = country.code
WHERE country.continent = 'Asia'
  AND countrylanguage.language = 'Chinese'
  AND countrylanguage.isofficial = 'T';
```
| name |
| --- |
| Shanghai |
| Peking |
| Chongqing |
| Tianjin |
| Wuhan |
| Harbin |
| Shenyang |
| Kanton [Guangzhou] |
| Chengdu |
| Nanking [Nanjing] |
| Changchun |
| Xi´an |
| Dalian |
| Qingdao |
| Jinan |
| Hangzhou |
| Zhengzhou |
| Shijiazhuang |
| Taiyuan |
| Kunming |
| Changsha |
| Nanchang |
| Fuzhou |
| Lanzhou |
| Guiyang |
| Ningbo |
| Hefei |
| Urumtši [Ürümqi] |
| Anshan |
| Fushun |
| Nanning |
| Zibo |
| Qiqihar |
| Jilin |
| Tangshan |
| Baotou |
| Shenzhen |
| Hohhot |
| Handan |
| Wuxi |
| Xuzhou |
| Datong |
| Yichun |
| Benxi |
| Luoyang |
| Suzhou |
| Xining |
| Huainan |
| Jixi |
| Daqing |
| Fuxin |
| Amoy [Xiamen] |
| Liuzhou |
| Shantou |
| Jinzhou |
| Mudanjiang |
| Yinchuan |
| Changzhou |
| Zhangjiakou |
| Dandong |
| Hegang |
| Kaifeng |
| Jiamusi |
| Liaoyang |
| Hengyang |
| Baoding |
| Hunjiang |
| Xinxiang |
| Huangshi |
| Haikou |
| Yantai |
| Bengbu |
| Xiangtan |
| Weifang |
| Wuhu |
| Pingxiang |
| Yingkou |
| Anyang |
| Panzhihua |
| Pingdingshan |
| Xiangfan |
| Zhuzhou |
| Jiaozuo |
| Wenzhou |
| Zhangjiang |
| Zigong |
| Shuangyashan |
| Zaozhuang |
| Yakeshi |
| Yichang |
| Zhenjiang |
| Huaibei |
| Qinhuangdao |
| Guilin |
| Liupanshui |
| Panjin |
| Yangquan |
| Jinxi |
| Liaoyuan |
| Lianyungang |
| Xianyang |
| Tai´an |
| Chifeng |
| Shaoguan |
| Nantong |
| Leshan |
| Baoji |
| Linyi |
| Tonghua |
| Siping |
| Changzhi |
| Tengzhou |
| Chaozhou |
| Yangzhou |
| Dongwan |
| Ma´anshan |
| Foshan |
| Yueyang |
| Xingtai |
| Changde |
| Shihezi |
| Yancheng |
| Jiujiang |
| Dongying |
| Shashi |
| Xintai |
| Jingdezhen |
| Tongchuan |
| Zhongshan |
| Shiyan |
| Tieli |
| Jining |
| Wuhai |
| Mianyang |
| Luzhou |
| Zunyi |
| Shizuishan |
| Neijiang |
| Tongliao |
| Tieling |
| Wafangdian |
| Anqing |
| Shaoyang |
| Laiwu |
| Chengde |
| Tianshui |
| Nanyang |
| Cangzhou |
| Yibin |
| Huaiyin |
| Dunhua |
| Yanji |
| Jiangmen |
| Tongling |
| Suihua |
| Gongziling |
| Xiantao |
| Chaoyang |
| Ganzhou |
| Huzhou |
| Baicheng |
| Shangzi |
| Yangjiang |
| Qitaihe |
| Gejiu |
| Jiangyin |
| Hebi |
| Jiaxing |
| Wuzhou |
| Meihekou |
| Xuchang |
| Liaocheng |
| Haicheng |
| Qianjiang |
| Baiyin |
| Bei´an |
| Yixing |
| Laizhou |
| Qaramay |
| Acheng |
| Dezhou |
| Nanping |
| Zhaoqing |
| Beipiao |
| Fengcheng |
| Fuyu |
| Xinyang |
| Dongtai |
| Yuci |
| Honghu |
| Ezhou |
| Heze |
| Daxian |
| Linfen |
| Tianmen |
| Yiyang |
| Quanzhou |
| Rizhao |
| Deyang |
| Guangyuan |
| Changshu |
| Zhangzhou |
| Hailar |
| Nanchong |
| Jiutai |
| Zhaodong |
| Shaoxing |
| Fuyang |
| Maoming |
| Qujing |
| Ghulja |
| Jiaohe |
| Puyang |
| Huadian |
| Jiangyou |
| Qashqar |
| Anshun |
| Fuling |
| Xinyu |
| Hanzhong |
| Danyang |
| Chenzhou |
| Xiaogan |
| Shangqiu |
| Zhuhai |
| Qingyuan |
| Aqsu |
| Xiaoshan |
| Zaoyang |
| Xinghua |
| Hami |
| Huizhou |
| Jinmen |
| Sanming |
| Ulanhot |
| Korla |
| Wanxian |
| Rui´an |
| Zhoushan |
| Liangcheng |
| Jiaozhou |
| Taizhou |
| Taonan |
| Pingdu |
| Ji´an |
| Longkou |
| Langfang |
| Zhoukou |
| Suining |
| Yulin |
| Jinhua |
| Liu´an |
| Shuangcheng |
| Suizhou |
| Ankang |
| Weinan |
| Longjing |
| Da´an |
| Lengshuijiang |
| Laiyang |
| Xianning |
| Dali |
| Anda |
| Jincheng |
| Longyan |
| Xichang |
| Wendeng |
| Hailun |
| Binzhou |
| Linhe |
| Wuwei |
| Duyun |
| Mishan |
| Shangrao |
| Changji |
| Meixian |
| Yushu |
| Tiefa |
| Huai´an |
| Leiyang |
| Zalantun |
| Weihai |
| Loudi |
| Qingzhou |
| Qidong |
| Huaihua |
| Luohe |
| Chuzhou |
| Kaiyuan |
| Linqing |
| Chaohu |
| Laohekou |
| Dujiangyan |
| Zhumadian |
| Linchuan |
| Jiaonan |
| Sanmenxia |
| Heyuan |
| Manzhouli |
| Lhasa |
| Lianyuan |
| Kuytun |
| Puqi |
| Hongjiang |
| Qinzhou |
| Renqiu |
| Yuyao |
| Guigang |
| Kaili |
| Yan´an |
| Beihai |
| Xuangzhou |
| Quzhou |
| Yong´an |
| Zixing |
| Liyang |
| Yizheng |
| Yumen |
| Liling |
| Yuncheng |
| Shanwei |
| Cixi |
| Yuanjiang |
| Bozhou |
| Jinchang |
| Fu´an |
| Suqian |
| Shishou |
| Hengshui |
| Danjiangkou |
| Fujin |
| Sanya |
| Guangshui |
| Huangshan |
| Xingcheng |
| Zhucheng |
| Kunshan |
| Haining |
| Pingliang |
| Fuqing |
| Xinzhou |
| Jieyang |
| Zhangjiagang |
| Tong Xian |
| Ya´an |
| Emeishan |
| Enshi |
| Bose |
| Yuzhou |
| Tumen |
| Putian |
| Linhai |
| Xilin Hot |
| Shaowu |
| Junan |
| Huaying |
| Pingyi |
| Huangyan |
| Singapore |

**GOLD:**
```sql
SELECT DISTINCT city.name
FROM country
JOIN countrylanguage ON country.code = countrylanguage.countrycode
JOIN city ON country.code = city.countrycode
WHERE countrylanguage.isofficial = 't'
  AND countrylanguage.language = 'chinese'
  AND country.continent = 'asia'
```

| name |
| --- |

### 20. entry-584
**Question:** What are the first names of the students who live in Haiti permanently or have the cell phone number 09700166582 ?

**Difficulty:** hard

**DB Info:** student_transcripts_tracking
```
# addresses ( address_id , line_1 , line_2 , line_3 , city , zip_postcode , state_province_county , country , other_address_details )
# courses ( course_id , course_name , course_description , other_details )
# departments ( department_id , department_name , department_description , other_details )
# degree_programs ( degree_program_id , department_id , degree_summary_name , degree_summary_description , other_details )
# sections ( section_id , course_id , section_name , section_description , other_details )
# semesters ( semester_id , semester_name , semester_description , other_details )
# students ( student_id , current_address_id , permanent_address_id , first_name , middle_name , last_name , cell_mobile_number , email_address , ssn , date_first_registered , date_left , other_student_details )
# student_enrolment ( student_enrolment_id , degree_program_id , semester_id , student_id , other_details )
# student_enrolment_courses ( student_course_id , course_id , student_enrolment_id )
# transcripts ( transcript_id , transcript_date , other_details )
# transcript_contents ( student_course_id , transcript_id )
# degree_programs.department_id = departments.department_id
# sections.course_id = courses.course_id
# students.permanent_address_id = addresses.address_id
# students.current_address_id = addresses.address_id
# student_enrolment.student_id = students.student_id
# student_enrolment.semester_id = semesters.semester_id
# student_enrolment.degree_program_id = degree_programs.degree_program_id
# student_enrolment_courses.student_enrolment_id = student_enrolment.student_enrolment_id
# student_enrolment_courses.course_id = courses.course_id
# transcript_contents.transcript_id = transcripts.transcript_id
# transcript_contents.student_course_id = student_enrolment_courses.student_course_id
```
**SQLChatGPT:**
```sql
SELECT DISTINCT s.first_name
FROM students AS s
LEFT JOIN addresses AS a ON s.permanent_address_id = a.address_id
WHERE a.country = 'Haiti'
  OR s.cell_mobile_number = '09700166582';
```
| first_name |
| --- |
| Hobart |
| Warren |
| Jarvis |
| Delaney |

**GOLD:**
```sql
SELECT students.first_name
FROM students
JOIN addresses ON students.permanent_address_id = addresses.address_id
WHERE addresses.country = 'haiti'
  OR students.cell_mobile_number = '09700166582'
```

| first_name |
| --- |
| Jarvis |

### 21. entry-455
**Question:** List the first and last name of all players in the order of birth date.

**Difficulty:** medium

**DB Info:** wta_1
```
# players ( player_id , first_name , last_name , hand , birth_date , country_code )
# matches ( best_of , draw_size , loser_age , loser_entry , loser_hand , loser_ht , loser_id , loser_ioc , loser_name , loser_rank , loser_rank_points , loser_seed , match_num , minutes , round , score , surface , tourney_date , tourney_id , tourney_level , tourney_name , winner_age , winner_entry , winner_hand , winner_ht , winner_id , winner_ioc , winner_name , winner_rank , winner_rank_points , winner_seed , year )
# rankings ( ranking_date , ranking , player_id , ranking_points , tours )
# matches.winner_id = players.player_id
# matches.loser_id = players.player_id
# rankings.player_id = players.player_id
```
**SQLChatGPT:**
```sql
SELECT first_name,
       last_name
FROM players
ORDER BY birth_date ASC;
```
No results

**GOLD:**
```sql
SELECT first_name,
       last_name
FROM players
ORDER BY birth_date ASC
```

No results

### 22. entry-631
**Question:** Find the package choice and series name of the TV channel that has high definition TV.

**Difficulty:** medium

**DB Info:** tvshow
```
# tv_channel ( id , series_name , country , language , content , pixel_aspect_ratio_par , hight_definition_tv , pay_per_view_ppv , package_option )
# tv_series ( id , episode , air_date , rating , share , 18_49_rating_share , viewers_m , weekly_rank , channel )
# cartoon ( id , title , directed_by , written_by , original_air_date , production_code , channel )
# tv_series.channel = tv_channel.id
# cartoon.channel = tv_channel.id
```
**SQLChatGPT:**
```sql
SELECT package_option,
       series_name
FROM tv_channel
WHERE high_definition_tv = 'Yes';
```
No results

**GOLD:**
```sql
SELECT package_option,
       series_name
FROM tv_channel
WHERE hight_definition_tv = 'yes'
```

| package_option | series_name |
| --- | --- |
| Sky Famiglia + Sky HD | MTV Live HD |

### 23. entry-557
**Question:** Who is the earliest graduate of the school? List the first name, middle name and last name.

**Difficulty:** medium

**DB Info:** student_transcripts_tracking
```
# addresses ( address_id , line_1 , line_2 , line_3 , city , zip_postcode , state_province_county , country , other_address_details )
# courses ( course_id , course_name , course_description , other_details )
# departments ( department_id , department_name , department_description , other_details )
# degree_programs ( degree_program_id , department_id , degree_summary_name , degree_summary_description , other_details )
# sections ( section_id , course_id , section_name , section_description , other_details )
# semesters ( semester_id , semester_name , semester_description , other_details )
# students ( student_id , current_address_id , permanent_address_id , first_name , middle_name , last_name , cell_mobile_number , email_address , ssn , date_first_registered , date_left , other_student_details )
# student_enrolment ( student_enrolment_id , degree_program_id , semester_id , student_id , other_details )
# student_enrolment_courses ( student_course_id , course_id , student_enrolment_id )
# transcripts ( transcript_id , transcript_date , other_details )
# transcript_contents ( student_course_id , transcript_id )
# degree_programs.department_id = departments.department_id
# sections.course_id = courses.course_id
# students.permanent_address_id = addresses.address_id
# students.current_address_id = addresses.address_id
# student_enrolment.student_id = students.student_id
# student_enrolment.semester_id = semesters.semester_id
# student_enrolment.degree_program_id = degree_programs.degree_program_id
# student_enrolment_courses.student_enrolment_id = student_enrolment.student_enrolment_id
# student_enrolment_courses.course_id = courses.course_id
# transcript_contents.transcript_id = transcripts.transcript_id
# transcript_contents.student_course_id = student_enrolment_courses.student_course_id
```
**SQLChatGPT:**
```sql
SELECT s.first_name,
       s.middle_name,
       s.last_name
FROM students s
JOIN student_enrolment se ON s.student_id = se.student_id
JOIN student_enrolment_courses sec ON se.student_enrolment_id = sec.student_enrolment_id
JOIN transcript_contents tc ON sec.student_course_id = tc.student_course_id
JOIN transcripts t ON tc.transcript_id = t.transcript_id
ORDER BY t.transcript_date ASC
LIMIT 1;
```
| first_name | middle_name | last_name |
| --- | --- | --- |
| Reva | Golda | Osinski |

**GOLD:**
```sql
SELECT first_name,
       middle_name,
       last_name
FROM students
ORDER BY date_left ASC
LIMIT 1
```

| first_name | middle_name | last_name |
| --- | --- | --- |
| Timmothy | Anna | Ward |

### 24. entry-821
**Question:** Return the codes of countries for which Spanish is the predominantly spoken language.

**Difficulty:** medium

**DB Info:** world_1
```
# city ( id , name , countrycode , district , population )
# sqlite_sequence ( name , seq )
# country ( code , name , continent , region , surfacearea , indepyear , population , lifeexpectancy , gnp , gnpold , localname , governmentform , headofstate , capital , code2 )
# countrylanguage ( countrycode , language , isofficial , percentage )
# city.countrycode = country.code
# countrylanguage.countrycode = country.code
```
**SQLChatGPT:**
```sql
SELECT cl.countrycode
FROM countrylanguage cl
JOIN
  (SELECT countrycode,
          MAX(percentage) AS max_percentage
   FROM countrylanguage
   WHERE LANGUAGE = 'Spanish'
   GROUP BY countrycode) AS subq ON cl.countrycode = subq.countrycode
AND cl.percentage = subq.max_percentage
WHERE cl.language = 'Spanish';
```
| countrycode |
| --- |
| ABW |
| AND |
| ARG |
| BLZ |
| BOL |
| CAN |
| CHL |
| COL |
| CRI |
| CUB |
| DOM |
| ECU |
| ESP |
| FRA |
| GTM |
| HND |
| MEX |
| NIC |
| PAN |
| PER |
| PRI |
| PRY |
| SLV |
| SWE |
| URY |
| USA |
| VEN |
| VIR |

**GOLD:**
```sql
SELECT countrycode,
       MAX (percentage)
FROM countrylanguage
WHERE LANGUAGE = 'Spanish'
GROUP BY countrycode
```

| countrycode | max (percentage) |
| --- | --- |
| ABW | 7.4 |
| AND | 44.6 |
| ARG | 96.8 |
| BLZ | 31.6 |
| BOL | 87.7 |
| CAN | 0.7 |
| CHL | 89.7 |
| COL | 99.0 |
| CRI | 97.5 |
| CUB | 100.0 |
| DOM | 98.0 |
| ECU | 93.0 |
| ESP | 74.4 |
| FRA | 0.4 |
| GTM | 64.7 |
| HND | 97.2 |
| MEX | 92.1 |
| NIC | 97.6 |
| PAN | 76.8 |
| PER | 79.8 |
| PRI | 51.3 |
| PRY | 55.1 |
| SLV | 100.0 |
| SWE | 0.6 |
| URY | 95.7 |
| USA | 7.5 |
| VEN | 96.9 |
| VIR | 13.3 |

### 25. entry-213
**Question:** How many flights does airline 'JetBlue Airways' have?

**Difficulty:** medium

**DB Info:** flight_2
```
# airlines ( uid , airline , abbreviation , country )
# airports ( city , airportcode , airportname , country , countryabbrev )
# flights ( airline , flightno , sourceairport , destairport )
# flights.destairport = airports.airportcode
# flights.sourceairport = airports.airportcode
```
**SQLChatGPT:**
```sql
SELECT COUNT(*)
FROM flights
WHERE airline = 'JetBlue Airways';
```
| count(*) |
| --- |
| 0 |

**GOLD:**
```sql
SELECT COUNT (*)
FROM flights
JOIN airlines ON flights.airline = airlines.uid
WHERE airlines.airline = 'JetBlue Airways'
```

| count (*) |
| --- |
| 100 |

