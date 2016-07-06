package decide.crawler

/**
 * @author jlafuente
 */
object Fetcher {
  def Fecth(city : City) : String = {
    Console.println("Reading forecast from city " + city.name)
    
    val url = "http://api.openweathermap.org/data/2.5/weather?id=" + city.id + "&APPID=f234717e52691e1967f6ba6e16c72a11"
    val result = scala.io.Source.fromURL(url, "UTF-8").mkString
    
    result
  }  
  
  def Fetch(cities : List[City]) : List[(City, String)] = {
    for ( city <- cities ) yield (city, Fetcher.Fecth(city))
  }  
}