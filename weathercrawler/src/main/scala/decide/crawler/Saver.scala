package decide.crawler

import java.util.Calendar
import java.nio.file.Paths
import java.nio.file.Files
import java.io.PrintWriter
import java.io.File
import java.text.SimpleDateFormat
import org.json4s.native.JsonMethods
import org.json4s._
import org.json4s.native.JsonMethods._


/**
 * @author jlafuente
 */

object Saver {
  val calendar = Calendar.getInstance

  def saveResults(rootDir: String, forecast: (City, String)) {
    val (city, json) = forecast

    val parsed = JsonMethods.parse(json)
    val dt = compact(render(parsed \ "dt"))
    calendar.setTimeInMillis(dt.toLong*1000)
    
    val fileName = rootDir + "/" + city.name + "/" + calendar.get(Calendar.YEAR) + "/" + new SimpleDateFormat("dd-MMM").format(calendar.getTime) + "/" + city.name + "_" + calendar.get(Calendar.HOUR_OF_DAY)+ "_" + + calendar.get(Calendar.MINUTE) + ".json"

    val file = new File(fileName)
    file.getParentFile.mkdirs()
    file.createNewFile()

    val pw = new PrintWriter(file)
    pw.print(json)
    pw.close();
  }

  def main(args: Array[String]) {
    val dataDir = args(0)
    val resultsDir = args(1)
    
    val allCities = Cities.read(dataDir + "/" + "city.list.json")

    val cityNames = Cities.readNames(dataDir + "/" + "cities.txt")

    val (cities, absent) = allCities.get(cityNames)

    if ( absent != Nil )
      Console.println("WARNING: It was not possible to obtain data from the following cities: " + absent)
    
    while (true) { 
      Console.println("30 min Loop")
      
      val forecast = Fetcher.Fetch(cities)

      forecast.foreach(saveResults(resultsDir, _))
    
      Thread sleep 1800000 
    }
  }
}