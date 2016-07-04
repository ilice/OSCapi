package decide.crawler

import org.json4s.native.JsonMethods
import scala.io.Source
import java.io.InputStream
import java.io.File
import org.json4s.JsonAST._
import java.io.BufferedReader
import java.io.InputStreamReader
import scala.collection.immutable.Map

object Cities {
  def removeTilde ( str : String ) : String = {
    def noTilde( c : Char ) : Char = {
      val conversions = Map(('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'))

      val conversion = conversions.get(c)

      conversion.getOrElse(c)
    }
    
    
    val lowercasestr = str.toLowerCase() 
    
    lowercasestr.map { x => noTilde(x) }
  }
  
  def read(fileName: String): Cities = {
    val file = new File(fileName)

    val cities = for { line <- Source.fromFile(file, "UTF-8").getLines() } yield (Cities.parse(line))
    
    new Cities(cities.toList)
  }
  
  def readNames(fileName : String ) : List[String] = {
    val file = new File(fileName)

    val cities = for { line <- Source.fromFile(file, "UTF-8").getLines() } yield (Cities.removeTilde(line))

    cities.toList
  }

  def parse(line: String): City = {

    val parsed = JsonMethods.parse(line)

    val city = for {
      JObject(city) <- parsed
      JField("_id", JInt(id)) <- city
      JField("name", JString(name)) <- city
      JField("country", JString(country)) <- city
    } yield (new City(id, Cities.removeTilde(name), country))

    city.head
  }
}

class Cities(val cities: List[City]) {
  def find(name : String, country : String) : City = {
    val result = for {
      city <- cities
      if city.name == name && city.country == country
    } yield city;
    
    if ( result != Nil ) result.head else null
  }
  
  def get(cityNames: List[String]): (List[City], List[String]) = {
    val unfilteredCities = for { name <- cityNames } yield (find(name, "ES"))
    
    val cities = unfilteredCities.filter { x => x != null }
    
    val selectedNames = cities.map { city => city.name }

    val absent = cityNames.filter { x => !selectedNames.contains(x) }
    
    (cities, absent)
  }
}