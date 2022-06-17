# Convert PlantUML file to Diagrams.net XML file

This is a functional perl script used to demonstrate how to convert a file with PlantUML code into a Diagrams.net (a.k.a Draw.io) XML file from the command line. The PlantUML code and rendered SVG are embedded into the Diagrams.net/Draw.io document.

In the Diagrams.net or Draw.io program, the PlantUML diagram can be double-clicked on to see the PlantUML source code. If the PlantUML library is loaded, the PlantUML code can be edited and saved which will update the diagram.

This perl script requires java and the PlantUML compiled Jar. It was last tested with Java 17, PlantUML 1.2022.5, and Draw.io 20.0.1.

## Download PlantUML jar library

https://plantuml.com/download

## Create a PlantUML file

```bash
@startuml
Cat -> Mouse : eats
@enduml
```

## Convert a PlantUML file to a Diagrams.net xml file.

```bash
system> ./plantuml_to_drawio_xml.pl cat-eats-mouse.plantuml > cat-eats-mouse.drawio.xml
```

## Import or Load the draw.io xml file

* in diagrams.net open new
  * File > Open from > Device...
    * choose the file cat-eats-mouse.drawio.xml

* in diagrams.net import into existing document
  * File > Import from > Device...
    * choose the file cat-eats-mouse.drawio.xml

## Conversion steps

Comments in the code describe the steps to convert PlantUML to Diagram.net or Draw.io xml file

1. Convert PlantUML plain text data to SVG data using java and the PlantUML jar
1. Encode the PlantUML SVG data using Base64
1. Encode the PlantUML text data for XML/HTML/URL format
1. Obtain the SVG dimensions from he SVG data to add into the Draw.io XML parameters
1. Obtain the last modified date of the PlantUML file to set as the revision date in the Draw.io XML parameters
1. Create the Draw.io XML file and output to standard out

## Configuration

There are several properties that can be changed in the plantuml_to_drawio_xml.pl file. Open the file and look at the top. The path to Java and the PlantUML jar can be changed as well as a few Draw.io ID properties.

## License

Apache License 2.0, see [LICENSE](https://www.apache.org/licenses/LICENSE-2.0).

This program is free software
