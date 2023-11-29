### 1. entry-548
**Question:** What is the name of the course with the most students enrolled?

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
SELECT courses.course_name
FROM student_enrolment_courses
JOIN courses ON student_enrolment_courses.course_id = courses.course_id
GROUP BY student_enrolment_courses.course_id
ORDER BY COUNT(student_enrolment_courses.student_course_id) DESC
LIMIT 1;
```

| course_name |
| --- |
| pl |

**GOLD:**
```sql
SELECT T1.course_name
FROM Courses AS T1
JOIN Student_Enrolment_Courses AS T2 ON T1.course_id = T2.course_id
GROUP BY T1.course_name
ORDER BY count(*) DESC
LIMIT 1
```

| course_name |
| --- |
| rs |

**Analysis:**
- The problem seems to be the GROUP BY clause. The predicted query should group by the same column that is selected in the SELECT clause.
- The predicted query is answering the question correctly. The COUNT(student_enrolment_courses.student_course_id) is the number of students enrolled in the course. The number of students enrolled in 'pl' is 2 and the number of students in enrolled in 'rs' is also 2. The predicted query's GROUP BY clause is just grouping in a different way than the gold query.

| course_name | count(*) |
|-------------|----------|
| rs          | 2        |
| pl          | 2        |
| ml          | 2        |
| math        | 2        |
| la          | 2        |


### 2. entry-945
**Question:** Which professionals have operated a treatment that costs less than the average? Give me theor first names and last names.

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
SELECT DISTINCT professionals.first_name,
                professionals.last_name
FROM professionals
JOIN treatments ON professionals.professional_id = treatments.professional_id
WHERE treatments.cost_of_treatment <
    (SELECT AVG(treatments.cost_of_treatment)
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
SELECT DISTINCT T1.first_name,
                T1.last_name
FROM Professionals AS T1
JOIN Treatments AS T2
WHERE cost_of_treatment <
    (SELECT avg(cost_of_treatment)
     FROM Treatments)
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

**Analysis:**
- The GOLD query is wrong??
- The predicted query has completely different results for seemingly the same query. The difference is that the GOLD query does not JOIN the tables ON the professional_id, while the predicted query does. This actually makes the GOLD query wrong, because it is not joining the tables on the professional_id. This will cause the GOLD results to contain professionals who never completed a treatment, hence their average cost_of_treatment will be 0. The predicted query is correct because it is joining the tables on the professional_id, so it will only return professionals who have completed a treatment.

### 3. entry-537
**Question:** Find the kind of program which most number of students are enrolled in?

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
SELECT degree_programs.degree_summary_name
FROM students
JOIN student_enrolment ON students.student_id = student_enrolment.student_id
JOIN degree_programs ON student_enrolment.degree_program_id = degree_programs.degree_program_id
GROUP BY student_enrolment.degree_program_id
ORDER BY COUNT (*) DESC
LIMIT 1;
```
| degree_summary_name |
| --- |
| Bachelor |

**GOLD:**
```sql
SELECT T1.degree_summary_name
FROM Degree_Programs AS T1
JOIN Student_Enrolment AS T2 ON T1.degree_program_id = T2.degree_program_id
GROUP BY T1.degree_summary_name
ORDER BY count(*) DESC
LIMIT 1
```

| degree_summary_name |
| --- |
| Bachelor |

**Analysis:**
- The results are the same for both queries, so this should be considered correct. But both of the evaluation tools mark it wrong for some reason.
- It is marked wrong on the simple evaluation tool even though the results are the same, the simple evaluation tool only compares the result tables, so I dont know why it is marked wrong there too.
- The problem seems to be the GROUP BY clause. The predicted query should group by the same column that is selected in the SELECT clause.

### 4. entry-740
**Question:** What is name of the country that speaks the largest number of languages?

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
FROM countrylanguage
JOIN country ON countrylanguage.countrycode = country.code
GROUP BY countrylanguage.countrycode
ORDER BY COUNT(DISTINCT countrylanguage.language) DESC
LIMIT 1;
```
| name |
| --- |
| Canada |

**GOLD:**
```sql
SELECT T1.Name
FROM country AS T1
JOIN countrylanguage AS T2 ON T1.Code = T2.CountryCode
GROUP BY T1.Name
ORDER BY COUNT(*) DESC
LIMIT 1
```

| name |
| --- |
| United States |

**Analysis:**
- The COUNT of the number of languages each country speaks is the same for 5 different countries.

| Name              | COUNT(*) |
|-------------------|----------|
| United States     | 12       |
| Russian Federation| 12       |
| India             | 12       |
| China             | 12       |
| Canada            | 12       |

- The GOLD query says United States should be the correct answer, but the predicted query says Canada should be the correct answer. But both have the same number of languages, so they should both be correct.
- The problem seems to be the GROUP BY statement again. The predicted query is grouping by countrylanguage.countrycode, while the gold query is grouping by country.name.
- GROUPING BY the same column that is selected in the SELECT should be the norm.

### 5. entry-784
**Question:** Which cities are in European countries where English is not the official language?

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
SELECT city.name
FROM city
JOIN country ON city.countrycode = country.code
LEFT JOIN countrylanguage ON country.code = countrylanguage.countrycode
AND countrylanguage.language = 'English'
WHERE country.continent = 'Europe'
  AND countrylanguage.language IS NULL;
```
| name |
| --- |
| Tirana |
| Andorra la Vella |
| Wien |
| Graz |
| Linz |
| Salzburg |
| Innsbruck |
| Klagenfurt |
| ~700 more rows |


**GOLD:**
```sql
SELECT DISTINCT T2.Name
FROM country AS T1
JOIN city AS T2 ON T2.CountryCode = T1.Code
WHERE T1.Continent = 'Europe'
  AND T1.Name NOT IN
    (SELECT T3.Name
     FROM country AS T3
     JOIN countrylanguage AS T4 ON T3.Code = T4.CountryCode
     WHERE T4.IsOfficial = 'T'
       AND T4.Language = 'English')
```

| name |
| --- |
| Amsterdam |
| Rotterdam |
| Haag |
| Utrecht |
| Eindhoven |
| Tilburg |
| Groningen |
| Breda |
| ~700 more rows |

**Analysis:**
- The SQLChatGPT query uses a left join with the countrylanguage table and checks for NULL values in countrylanguage.language. This approach has two potential issues:
  1. It might miss cities in countries where English is an official language but is not listed in the countrylanguage table. This could happen due to incomplete data.
  2. It might include cities from countries where English is listed in the countrylanguage table but not marked as an official language. In this case, since the query checks for NULL values, it would ignore any non-null entries for English, whether it's official or not.

### 6. entry-538
**Question:** What is the degree summary name that has the most number of students enrolled?

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
SELECT degree_programs.degree_summary_name
FROM student_enrolment
JOIN degree_programs ON student_enrolment.degree_program_id = degree_programs.degree_program_id
GROUP BY student_enrolment.degree_program_id
ORDER BY COUNT (*) DESC
LIMIT 1;
```
| degree_summary_name |
| --- |
| Bachelor |

**GOLD:**
```sql
SELECT T1.degree_summary_name
FROM Degree_Programs AS T1
JOIN Student_Enrolment AS T2 ON T1.degree_program_id = T2.degree_program_id
GROUP BY T1.degree_summary_name
ORDER BY count(*) DESC
LIMIT 1
```

| degree_summary_name |
| --- |
| Bachelor |

**Analysis:**
- The results are the same for both queries, so this should be considered correct. But both of the evaluation tools mark it wrong for some reason.
- The problem seems to be the GROUP BY clause again. The predicted query should group by the same column that is selected in the SELECT clause.

### 7. entry-764
**Question:** What is average life expectancy in the countries where English is not the official language?

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
SELECT AVG(lifeexpectancy)
FROM country
WHERE code NOT IN
    (SELECT countrycode
     FROM countrylanguage
     WHERE isofficial = 'T'
       AND LOWER(LANGUAGE) = 'english' );
```
| avg(lifeexpectancy) |
| --- |
| 65.48270270270272 |

**GOLD:**
```sql
SELECT avg(LifeExpectancy)
FROM country
WHERE Name NOT IN
    (SELECT T1.Name
     FROM country AS T1
     JOIN countrylanguage AS T2 ON T1.Code = T2.CountryCode
     WHERE T2.Language = "English"
       AND T2.IsOfficial = "T")
```

| avg(lifeexpectancy) |
| --- |
| 65.48270270270272 |

**Analysis:**
- The answers are the same for both queries, so this should be considered correct. It is marked correct on the simple evaluation tool.
- Even using different database values, the answers are the same.

### 8. entry-102
**Question:** What is the maker of the carr produced in the earliest year and what year was it?

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
SELECT cm.maker,
       cd.year
FROM car_makers cm
JOIN model_list ml ON cm.id = ml.maker
JOIN car_names cn ON ml.model = cn.model
JOIN cars_data cd ON cn.makeid = cd.id
WHERE cd.year =
    (SELECT MIN(YEAR)
     FROM cars_data);
```
| maker | year |
| --- | --- |
| gm | 1970 |
| gm | 1970 |
| chrysler | 1970 |
| amc | 1970 |
| ford | 1970 |
| ford | 1970 |
| gm | 1970 |
| chrysler | 1970 |
| gm | 1970 |
| amc | 1970 |
| citroen | 1970 |
| gm | 1970 |
| ford | 1970 |
| chrysler | 1970 |
| amc | 1970 |
| chrysler | 1970 |
| chrysler | 1970 |
| ford | 1970 |
| gm | 1970 |
| gm | 1970 |
| toyota | 1970 |
| chrysler | 1970 |
| amc | 1970 |
| ford | 1970 |
| nissan | 1970 |
| volkswagen | 1970 |
| peugeaut | 1970 |
| volkswagen | 1970 |
| saab | 1970 |
| bmw | 1970 |
| amc | 1970 |
| ford | 1970 |
| gm | 1970 |
| chrysler | 1970 |

**GOLD:**
```sql
SELECT T2.Make,
       T1.Year
FROM CARS_DATA AS T1
JOIN CAR_NAMES AS T2 ON T1.Id = T2.MakeId
WHERE T1.Year =
    (SELECT min(YEAR)
     FROM CARS_DATA);
```

| make | year |
| --- | --- |
| chevrolet chevelle malibu | 1970 |
| buick skylark 320 | 1970 |
| plymouth satellite | 1970 |
| amc rebel sst | 1970 |
| ford torino | 1970 |
| ford galaxie 500 | 1970 |
| chevrolet impala | 1970 |
| plymouth fury iii | 1970 |
| pontiac catalina | 1970 |
| amc ambassador dpl | 1970 |
| citroen ds-21 pallas | 1970 |
| chevrolet chevelle concours (sw) | 1970 |
| ford torino (sw) | 1970 |
| plymouth satellite (sw) | 1970 |
| amc rebel sst (sw) | 1970 |
| dodge challenger se | 1970 |
| plymouth cuda 340 | 1970 |
| ford mustang boss 302 | 1970 |
| chevrolet monte carlo | 1970 |
| buick estate wagon (sw) | 1970 |
| toyota corona mark ii | 1970 |
| plymouth duster | 1970 |
| amc hornet | 1970 |
| ford maverick | 1970 |
| datsun pl510 | 1970 |
| volkswagen 1131 deluxe sedan | 1970 |
| peugeot 504 | 1970 |
| audi 100 ls | 1970 |
| saab 99e | 1970 |
| bmw 2002 | 1970 |
| amc gremlin | 1970 |
| ford f250 | 1970 |
| chevy c20 | 1970 |
| dodge d200 | 1970 |
| hi 1200d | 1970 |

**Analysis:**
- The predicted query SELECTS the wrong columns. It should select cn.make and cd.year, but it selects cd.maker and cd.year.
- This query is corrected in my simple evaluation tool by changing the SELECT clause to the correct one.

### 9. entry-230
**Question:** What airline serves the most flights?

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
SELECT airlines.airline,
       COUNT(*) AS total_flights
FROM flights
JOIN airlines ON flights.airline = airlines.uid
GROUP BY flights.airline
ORDER BY total_flights DESC
LIMIT 1;
```
| airline | total_flights |
| --- | --- |
| United Airlines | 100 |

**GOLD:**
```sql
SELECT T1.Airline
FROM AIRLINES AS T1
JOIN FLIGHTS AS T2 ON T1.uid = T2.Airline
GROUP BY T1.Airline
ORDER BY count(*) DESC
LIMIT 1
```

| airline |
| --- |
| Virgin America |

**Analysis:**
- The predicted query is wrong because it is SELECTING an extra column for the count(*). For some reason this query is not correct by my SELECT clause repair in the simple evaluation tool.
- The GROUP BY is also incorrect again, it is grouping by flights.airline, but selecting airlines.airline. It should be grouping by airlines.airline.

| Airline          | count(*) |
|------------------|----------|
| Virgin America   | 100      |
| United Airlines  | 100      |


### 10. entry-420
**Question:** What are the id, name and membership level of visitors who have spent the largest amount of money in total in all museum tickets?

**Difficulty:** extra

**DB Info:** museum_visit
```
# museum ( museum_id , name , num_of_staff , open_year )
# visitor ( id , name , level_of_membership , age )
# visit ( museum_id , visitor_id , num_of_ticket , total_spent )
# visit.visitor_id = visitor.id
# visit.museum_id = museum.museum_id
```
**SQLChatGPT:**
```sql
SELECT visitor.id,
       visitor.name,
       visitor.level_of_membership
FROM visitor
JOIN visit ON visitor.id = visit.visitor_id
GROUP BY visitor.id,
         visitor.name,
         visitor.level_of_membership
ORDER BY SUM(visit.total_spent) DESC
LIMIT 1;
```
| id | name | level_of_membership |
| --- | --- | --- |
| 3 | Arjen Robben | 1 |

**GOLD:**
```sql
SELECT t2.visitor_id,
       t1.name,
       t1.Level_of_membership
FROM visitor AS t1
JOIN visit AS t2 ON t1.id = t2.visitor_id
GROUP BY t2.visitor_id
ORDER BY sum(t2.Total_spent) DESC
LIMIT 1
```

| visitor_id | name | level_of_membership |
| --- | --- | --- |
| 3 | Arjen Robben | 1 |

**Analysis:**
- The predicted query is correct with returning the same results as the gold query. It is not marked incorrect on the simple evaluation tool.
- For some reason it is marked incorrect on the offcial evaluation tool. I think it is because the predicted query is selecting visitor.name, but the gold query is selecting t1.name. The predicted query should be selecting t1.name.
  - It also could be a difference in the GROUP BY clauses.

### 11. entry-231
**Question:** Find the abbreviation and country of the airline that has fewest number of flights?

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
SELECT a.abbreviation,
       a.country
FROM airlines AS a
JOIN flights AS f ON a.uid = f.airline
GROUP BY a.abbreviation,
         a.country
ORDER BY COUNT(*) ASC
LIMIT 1;
```
| abbreviation | country |
| --- | --- |
| AirTran | USA |

**GOLD:**
```sql
SELECT T1.Abbreviation,
       T1.Country
FROM AIRLINES AS T1
JOIN FLIGHTS AS T2 ON T1.uid = T2.Airline
GROUP BY T1.Airline
ORDER BY count(*)
LIMIT 1
```

| abbreviation | country |
| --- | --- |
| AirTran | USA |

**Analysis:**
- The predicted query is correct with returning the same results as the gold query. It is not marked incorrect on the simple evaluation tool.
- It seems that once again, the GROUP BY clause is the problem for being marked correct on the official evaluation tool. The predicted query is grouping by a.abbreviation and a.country, while the gold query is grouping by a.airline. The predicted query should be grouping by a.airline.

### 12. entry-760
**Question:** Find the city with the largest population that uses English.

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
SELECT city.name,
       city.population
FROM city
JOIN countrylanguage ON city.countrycode = countrylanguage.countrycode
WHERE countrylanguage.language = 'English'
  AND countrylanguage.isofficial = 'T'
ORDER BY city.population DESC
LIMIT 1;
```
| name | population |
| --- | --- |
| New York | 8008278 |

**GOLD:**
```sql
SELECT T1.Name,
       T1.Population
FROM city AS T1
JOIN countrylanguage AS T2 ON T1.CountryCode = T2.CountryCode
WHERE T2.Language = "English"
ORDER BY T1.Population DESC
LIMIT 1
```

| name | population |
| --- | --- |
| New York | 8008278 |

**Analysis:**
- The predicted query is correct with returning the same results as the gold query. But it is still marked wrong on my simple evaluation even though the tables are exactly the same.
- The only difference in the queries is the extra WHERE condition `AND countrylanguage.isofficial = 'T'`


### 13. entry-505
**Question:** Show names, results and bulgarian commanders of the battles with no ships lost in the 'English Channel'.

**Difficulty:** extra

**DB Info:** battle_death
```
# battle ( id , name , date , bulgarian_commander , latin_commander , result )
# ship ( lost_in_battle , id , name , tonnage , ship_type , location , disposition_of_ship )
# death ( caused_by_ship_id , id , note , killed , injured )
# ship.lost_in_battle = battle.id
# death.caused_by_ship_id = ship.id
```
**SQLChatGPT:**
```sql
SELECT name,
       RESULT,
       bulgarian_commander
FROM battle
WHERE id NOT IN
    (SELECT lost_in_battle
     FROM ship
     WHERE LOCATION = 'English Channel'
       AND disposition_of_ship = 'lost' );
```
| name | result | bulgarian_commander |
| --- | --- | --- |
| Battle of Adrianople | Bulgarian victory | Kaloyan |
| Battle of Serres | Bulgarian victory | Kaloyan |
| Battle of Rusion | Bulgarian victory | Kaloyan |
| Battle of Rodosto | Bulgarian victory | Kaloyan |
| Battle of Messinopolis | Bulgarian victory | Unknown |
| Battle of Boruy | Bulgarian victory | Boril |
| Battle of Philippopolis | Latin victory | Boril |
| Siege of Constantinople | Two Year Truce | Ivan Asen II |

**GOLD:**
```sql
SELECT name,
       RESULT,
       bulgarian_commander
FROM battle
EXCEPT
SELECT T1.name,
       T1.result,
       T1.bulgarian_commander
FROM battle AS T1
JOIN ship AS T2 ON T1.id = T2.lost_in_battle
WHERE T2.location = 'English Channel'
```

| name | result | bulgarian_commander |
| --- | --- | --- |
| Battle of Adrianople | Bulgarian victory | Kaloyan |
| Battle of Rusion | Bulgarian victory | Kaloyan |
| Battle of Serres | Bulgarian victory | Kaloyan |

**Analysis:**
- The problem with the predicted query is the extra condition in the WHERE clause `AND disposition_of_ship = 'lost'`. There are no ships 'lost' (they are either 'captured', 'wrecked', 'sank, or 'scuttled') in the English Channel, so this condition will always be false, and the subquery will always return no rows. This will cause the predicted query to return all battles, while the gold query will return only battles that have no ships lost in the English Channel.

### 14. entry-936
**Question:** Which owner has paid for the most treatments on his or her dogs? List the owner id and last name.

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
SELECT owners.owner_id,
       owners.last_name
FROM owners
JOIN dogs ON owners.owner_id = dogs.owner_id
JOIN treatments ON dogs.dog_id = treatments.dog_id
GROUP BY owners.owner_id,
         owners.last_name
ORDER BY SUM(treatments.cost_of_treatment) DESC
LIMIT 1;
```
| owner_id | last_name |
| --- | --- |
| 3 | Stoltenberg |

**GOLD:**
```sql
SELECT T1.owner_id,
       T1.last_name
FROM Owners AS T1
JOIN Dogs AS T2 ON T1.owner_id = T2.owner_id
JOIN Treatments AS T3 ON T2.dog_id = T3.dog_id
GROUP BY T1.owner_id
ORDER BY count(*) DESC
LIMIT 1
```

| owner_id | last_name |
| --- | --- |
| 14 | Funk |

**Analysis:**
- The predicted query is wrong becuase it is summing the total cost of treatments for each owner, while the gold query is counting the number of treatments for each owner. The predicted query should be counting the number of treatments for each owner instead.
- This question is up to interpretation. The predicted query is correct in the sense that it is returning the owner who has paid the most for treatments on his or her dogs. But the gold query is correct in the sense that it is returning the owner who has paid for the most treatments on his or her dogs. The difference is that the predicted query is summing the total cost of treatments for each owner, while the gold query is counting the number of treatments for each owner.

### 15. entry-219
**Question:** How many United Airlines flights go to City 'Aberdeen'?

**Difficulty:** hard

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
SELECT COUNT (*)
FROM flights
JOIN airports ON flights.destairport = airports.airportcode
WHERE airports.city = 'Aberdeen'
  AND flights.airline = 'United Airlines';
```
| count (*) |
| --- |
| 0 |

**GOLD:**
```sql
SELECT count(*)
FROM FLIGHTS AS T1
JOIN AIRPORTS AS T2 ON T1.DestAirport = T2.AirportCode
JOIN AIRLINES AS T3 ON T3.uid = T1.Airline
WHERE T2.City = "Aberdeen"
  AND T3.Airline = "United Airlines"
```

| count(*) |
| --- |
| 0 |

**Analysis:**
- The predicted query is correct with returning the same results as the gold query. It is not marked incorrect on the simple evaluation tool.
- I have no idea why the official evaluation tool is saying they are inncorrect. The count is 0 on all different versions of this database.

### 16. entry-544
**Question:** What is the name of the semester with no students enrolled?

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
SELECT semester_name
FROM semesters
EXCEPT
SELECT semesters.semester_name
FROM semesters
JOIN student_enrolment ON semesters.semester_id = student_enrolment.semester_id;
```
| semester_name |
| --- |
| fall 2010 |
| spring 2013 |
| spring 2014 |
| spring 2016 |
| spring 2017 |
| winter 2018 |

**GOLD:**
```sql
SELECT semester_name
FROM Semesters
WHERE semester_id NOT IN
    (SELECT semester_id
     FROM Student_Enrolment)
```

| semester_name |
| --- |
| fall 2010 |
| spring 2013 |
| spring 2014 |
| spring 2016 |
| spring 2017 |
| winter 2018 |

**Analysis:**
- The predicted query is correct with returning the same results as the gold query. However, it is marked incorrect on the simple evaluation tool for some reason even though I am purly comparing the results of the queries.
- This should be marked correct on both evaluation tools.

### 17. entry-772
**Question:** What are the countries that have greater surface area than any country in Europe?

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
SELECT c.name
FROM country AS c
WHERE c.surfacearea >
    (SELECT MAX(c2.surfacearea)
     FROM country AS c2
     WHERE c2.continent = 'Europe' )
  AND c.continent <> 'Europe';
```
| name |
| --- |

**GOLD:**
```sql
SELECT Name
FROM country
WHERE SurfaceArea >
    (SELECT min(SurfaceArea)
     FROM country
     WHERE Continent = "Europe")
```

| name |
| --- |
| Aruba |
| Afghanistan |
| Angola |
| Anguilla |
| Albania |
| Andorra |
| Netherlands Antilles |
| United Arab Emirates |
| Argentina |
| Armenia |
| American Samoa |
| Antarctica |
| French Southern territories |
| Antigua and Barbuda |
| Australia |
| Austria |
| Azerbaijan |
| Burundi |
| Belgium |
| Benin |
| Burkina Faso |
| Bangladesh |
| Bulgaria |
| Bahrain |
| Bahamas |
| Bosnia and Herzegovina |
| Belarus |
| Belize |
| Bermuda |
| Bolivia |
| Brazil |
| Barbados |
| Brunei |
| Bhutan |
| Bouvet Island |
| Botswana |
| Central African Republic |
| Canada |
| Cocos (Keeling) Islands |
| Switzerland |
| Chile |
| China |
| Côte d’Ivoire |
| Cameroon |
| Congo, The Democratic Republic of the |
| Congo |
| Cook Islands |
| Colombia |
| Comoros |
| Cape Verde |
| Costa Rica |
| Cuba |
| Christmas Island |
| Cayman Islands |
| Cyprus |
| Czech Republic |
| Germany |
| Djibouti |
| Dominica |
| Denmark |
| Dominican Republic |
| Algeria |
| Ecuador |
| Egypt |
| Eritrea |
| Western Sahara |
| Spain |
| Estonia |
| Ethiopia |
| Finland |
| Fiji Islands |
| Falkland Islands |
| France |
| Faroe Islands |
| Micronesia, Federated States of |
| Gabon |
| United Kingdom |
| Georgia |
| Ghana |
| Gibraltar |
| Guinea |
| Guadeloupe |
| Gambia |
| Guinea-Bissau |
| Equatorial Guinea |
| Greece |
| Grenada |
| Greenland |
| Guatemala |
| French Guiana |
| Guam |
| Guyana |
| Hong Kong |
| Heard Island and McDonald Islands |
| Honduras |
| Croatia |
| Haiti |
| Hungary |
| Indonesia |
| India |
| British Indian Ocean Territory |
| Ireland |
| Iran |
| Iraq |
| Iceland |
| Israel |
| Italy |
| Jamaica |
| Jordan |
| Japan |
| Kazakstan |
| Kenya |
| Kyrgyzstan |
| Cambodia |
| Kiribati |
| Saint Kitts and Nevis |
| South Korea |
| Kuwait |
| Laos |
| Lebanon |
| Liberia |
| Libyan Arab Jamahiriya |
| Saint Lucia |
| Liechtenstein |
| Sri Lanka |
| Lesotho |
| Lithuania |
| Luxembourg |
| Latvia |
| Macao |
| Morocco |
| Monaco |
| Moldova |
| Madagascar |
| Maldives |
| Mexico |
| Marshall Islands |
| Macedonia |
| Mali |
| Malta |
| Myanmar |
| Mongolia |
| Northern Mariana Islands |
| Mozambique |
| Mauritania |
| Montserrat |
| Martinique |
| Mauritius |
| Malawi |
| Malaysia |
| Mayotte |
| Namibia |
| New Caledonia |
| Niger |
| Norfolk Island |
| Nigeria |
| Nicaragua |
| Niue |
| Netherlands |
| Norway |
| Nepal |
| Nauru |
| New Zealand |
| Oman |
| Pakistan |
| Panama |
| Pitcairn |
| Peru |
| Philippines |
| Palau |
| Papua New Guinea |
| Poland |
| Puerto Rico |
| North Korea |
| Portugal |
| Paraguay |
| Palestine |
| French Polynesia |
| Qatar |
| Réunion |
| Romania |
| Russian Federation |
| Rwanda |
| Saudi Arabia |
| Sudan |
| Senegal |
| Singapore |
| South Georgia and the South Sandwich Islands |
| Saint Helena |
| Svalbard and Jan Mayen |
| Solomon Islands |
| Sierra Leone |
| El Salvador |
| San Marino |
| Somalia |
| Saint Pierre and Miquelon |
| Sao Tome and Principe |
| Suriname |
| Slovakia |
| Slovenia |
| Sweden |
| Swaziland |
| Seychelles |
| Syria |
| Turks and Caicos Islands |
| Chad |
| Togo |
| Thailand |
| Tajikistan |
| Tokelau |
| Turkmenistan |
| East Timor |
| Tonga |
| Trinidad and Tobago |
| Tunisia |
| Turkey |
| Tuvalu |
| Taiwan |
| Tanzania |
| Uganda |
| Ukraine |
| United States Minor Outlying Islands |
| Uruguay |
| United States |
| Uzbekistan |
| Saint Vincent and the Grenadines |
| Venezuela |
| Virgin Islands, British |
| Virgin Islands, U.S. |
| Vietnam |
| Vanuatu |
| Wallis and Futuna |
| Samoa |
| Yemen |
| Yugoslavia |
| South Africa |
| Zambia |
| Zimbabwe |

**Analysis:**
- The predicted query is wrong becuase of a misunderstanding of the question.
  - The predicted query is returning all countries that have a surface area greater than the largest surface area of any country in Europe.
  - The gold query is returning all countries that have a surface area greater than the smallest surface area of any country in Europe.
- The predicted results are empty becuase there are no countries with a surface area greater than the largest surface area of any country in Europe.

### 18. entry-116
**Question:** What is the count of the car models produced in the United States?

**Difficulty:** hard

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
SELECT COUNT(*)
FROM car_names
JOIN model_list ON car_names.model = model_list.model
JOIN car_makers ON model_list.maker = car_makers.id
JOIN countries ON car_makers.country = countries.countryid
WHERE countries.countryname = 'United States';
```
| count(*) |
| --- |
| 0 |

**GOLD:**
```sql
SELECT count(*)
FROM MODEL_LIST AS T1
JOIN CAR_MAKERS AS T2 ON T1.Maker = T2.Id
JOIN COUNTRIES AS T3 ON T2.Country = T3.CountryId
WHERE T3.CountryName = 'usa';
```

| count(*) |
| --- |
| 13 |

**Analysis:**
- The predicted query JOINS the wrong tables. It should be joining model_list, car_makers, and countries. Instead it is joining car_names, model_list, car_makers, and countries.
- It also has the wrong WHERE condition. It should be `WHERE T3.CountryName = 'usa'`, but it is `WHERE countries.countryname = 'United States'`.

### 19. entry-64
**Question:** What are the ids of the students who do not own cats as pets?

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
SELECT DISTINCT student.stuid
FROM student
LEFT JOIN has_pet ON student.stuid = has_pet.stuid
LEFT JOIN pets ON has_pet.petid = pets.petid
WHERE pets.pettype != 'cat'
  OR pets.pettype IS NULL;
```
| stuid |
| --- |
| 1002 |
| 1003 |
| 1004 |
| 1005 |
| 1006 |
| 1007 |
| 1008 |
| 1009 |
| 1010 |
| 1011 |
| 1012 |
| 1014 |
| 1015 |
| 1016 |
| 1017 |
| 1018 |
| 1019 |
| 1020 |
| 1021 |
| 1022 |
| 1023 |
| 1024 |
| 1025 |
| 1026 |
| 1027 |
| 1028 |
| 1029 |
| 1030 |
| 1031 |
| 1032 |
| 1033 |
| 1034 |
| 1035 |

**GOLD:**
```sql
SELECT stuid
FROM student
EXCEPT
SELECT T1.stuid
FROM student AS T1
JOIN has_pet AS T2 ON T1.stuid = T2.stuid
JOIN pets AS T3 ON T3.petid = T2.petid
WHERE T3.pettype = 'cat'
```

| stuid |
| --- |
| 1002 |
| 1003 |
| 1004 |
| 1005 |
| 1006 |
| 1007 |
| 1008 |
| 1009 |
| 1010 |
| 1011 |
| 1012 |
| 1014 |
| 1015 |
| 1016 |
| 1017 |
| 1018 |
| 1019 |
| 1020 |
| 1021 |
| 1022 |
| 1023 |
| 1024 |
| 1025 |
| 1026 |
| 1027 |
| 1028 |
| 1029 |
| 1030 |
| 1031 |
| 1032 |
| 1033 |
| 1034 |
| 1035 |

**Analysis:**
- The predicted query is correct with returning the same results as the gold query. However, it is marked incorrect on the simple evaluation tool for some reason even though I am purly comparing the results of the queries.
- This should be marked correct on both evaluation tools.

### 20. entry-233
**Question:** What are airlines that have some flight departing from airport 'AHD'?

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
SELECT DISTINCT airlines.airline
FROM airlines
JOIN flights ON airlines.abbreviation = flights.airline
JOIN airports ON airports.airportcode = flights.sourceairport
WHERE airports.airportname = 'AHD';
```
| airline |
| --- |

**GOLD:**
```sql
SELECT T1.Airline
FROM AIRLINES AS T1
JOIN FLIGHTS AS T2 ON T1.uid = T2.Airline
WHERE T2.SourceAirport = "AHD"
```

| airline |
| --- |

**Analysis:**
- Even though the predicted query is returning the same results as the gold query it is still incorrect.
- The predicted query is incorrect becuase it uses the wrong WHERE condition. It should be `WHERE airports.airportcode = 'AHD'`, but it is `WHERE airports.airportname = 'AHD'`.

### 21. entry-48
**Question:** How much does the youngest dog weigh?

**Difficulty:** medium

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
SELECT weight
FROM pets
WHERE pettype = 'dog'
ORDER BY pet_age ASC
LIMIT 1;
```
| weight |
| --- |
| 9.3 |

**GOLD:**
```sql
SELECT weight
FROM pets
ORDER BY pet_age
LIMIT 1
```

| weight |
| --- |
| 9.3 |

**Analysis:**
- The predicted query is correct with returning the same results as the gold query. It is not marked incorrect on the simple evaluation tool. It is marked incorrect on the official evaluation tool.
- The GOLD query is actually wrong because it is not filtering for dogs. It should be `WHERE pettype = 'dog'`.



### 22. entry-408
**Question:** What are the names of the teachers who teach at least two courses?

**Difficulty:** medium

**DB Info:** course_teach
```
# course ( course_id , staring_date , course )
# teacher ( teacher_id , name , age , hometown )
# course_arrange ( course_id , teacher_id , grade )
# course_arrange.teacher_id = teacher.teacher_id
# course_arrange.course_id = course.course_id
```
**SQLChatGPT:**
```sql
SELECT teacher.name
FROM course_arrange
JOIN teacher ON course_arrange.teacher_id = teacher.teacher_id
GROUP BY course_arrange.teacher_id
HAVING COUNT (*) >= 2;
```
| name |
| --- |
| Anne Walker |

**GOLD:**
```sql
SELECT T2.Name
FROM course_arrange AS T1
JOIN teacher AS T2 ON T1.Teacher_ID = T2.Teacher_ID
GROUP BY T2.Name
HAVING COUNT(*) >= 2
```

| name |
| --- |
| Anne Walker |

**Analysis:**
- The predicted query is correct with returning the same results as the gold query. It is not marked incorrect on the simple evaluation tool. It is marked incorrect on the official evaluation tool.
- The problem must be the differing GROUP BY clauses. The predicted query is grouping by course_arrange.teacher_id, while the gold query is grouping by teacher.name. The predicted query should be grouping by the same column as the SELECT clause, teacher.name.

