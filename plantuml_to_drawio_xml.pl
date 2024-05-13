#!/usr/bin/perl

use strict;
use MIME::Base64;
use Time::gmtime;
use File::stat;
# use open qw( :encoding(UTF-8) :std ); # Set UTF-8 as the default encoding
use autodie;
use IPC::Open2;

BEGIN {
  use vars qw($JAVABIN $PLANTUMLJAR $DEBUG);
  $JAVABIN="java";
  $PLANTUMLJAR="plantuml-1.2024.4.jar";
  $DEBUG=0;
  use vars qw($DIO_AGENT_NAME $DIO_ETAG_ID $DIO_DIAGRAM_ID $DIO_USEROBJECT_ID);
  $DIO_AGENT_NAME    = "5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36";
  $DIO_ETAG_ID       = "ETAG111111111111xx01";
  $DIO_DIAGRAM_ID    = "DIAGRAM111111111xx01";
  $DIO_USEROBJECT_ID = "USEROBJECT111111xx01-1";
}

sub dprint (@) {
  print @_ if $DEBUG >= 1;
}

my $plantuml_file = shift;
my $cmd_err=0;
unless ( -f "$plantuml_file" ) {
  print "Usage: $0 <PlantUML-file>\n";
  $cmd_err++;
}
unless ( -f "$PLANTUMLJAR" ) {
  print "The java binary should be in the current path, and PlantUML jar in the current directory.\n";
  $cmd_err++;
}
exit 0 if $cmd_err;
my $i=1;

#
# Convert PlantUML plain text data to SVG data
#
# Read in PlantUML
my $plantuml_textdata;
my $plantuml_svgdata;
open (TPUML,"<$plantuml_file");
while (<TPUML>) {
  $plantuml_textdata .= "$_";
}
chomp($plantuml_textdata);
dprint ($i++,"PlantUML_Text=[$plantuml_textdata]\n");
close (TPUML);
#
# Convert PlantUML to SVG using PlanUML Java Library
my ($stdout,$stdin);
my $pid = open2($stdout, $stdin, "$JAVABIN -jar $PLANTUMLJAR -tsvg -pipe");
print $stdin "$plantuml_textdata\n";
close($stdin);
while (my $line = <$stdout>) {
  $plantuml_svgdata .= "$line";
  #last if "$line" =~ /\<\/svg\>/;
}
close($stdout);
waitpid $pid, 0;
dprint ($i++,"PlantUML_SVG=[$plantuml_svgdata]\n");

#
# base64 encode the PlantUML SVG data
#
my $plantuml_svgb64data = encode_base64($plantuml_svgdata, '');
dprint ($i++,"PlantUML_Base64=[$plantuml_svgb64data]\n");

#
# XML/HTML/URL encode the PlantUML text data
# Only 5 characters are needed to be escaped for XML, and include newlines and tabs
#
my $plantuml_escapedtextdata = $plantuml_textdata;
$plantuml_escapedtextdata =~ s/\&/\&amp;/g;
$plantuml_escapedtextdata =~ s/</\&lt;/g;
$plantuml_escapedtextdata =~ s/>/\&gt;/g;
$plantuml_escapedtextdata =~ s/"/\&quot;/g;
$plantuml_escapedtextdata =~ s/'"'"'/\&apos;/g;
$plantuml_escapedtextdata =~ s/\r\n/\\n/g;
$plantuml_escapedtextdata =~ s/\n/\\n/g;
$plantuml_escapedtextdata =~ s/\r/\\n/g; #lost carriage returns
$plantuml_escapedtextdata =~ s/\t/\\t/g;
dprint ($i++,"PlantUML_EscapedText=[$plantuml_escapedtextdata]\n");

#
# Obtain the SVG dimensions
#
my ($width,$height) = $plantuml_svgdata =~ /.*width:([\d]+px);height:([\d]+px);.*/;
dprint ($i++,"[width=$width,height=$height]\n");

#
# Set the Draw.io revision date to the last modified date of the PlantUML file
#
my $filegmtdate = gmtime(stat($plantuml_file)->mtime);
dprint ($i++,"[gmtime=$filegmtdate]\n");
my $year=($filegmtdate->year() + 1900);
my $month=sprintf("%02d",($filegmtdate->mon() +1));
my $mday=sprintf("%02d",$filegmtdate->mday());
my $hour=sprintf("%02d",$filegmtdate->hour());
my $min=sprintf("%02d",$filegmtdate->min());
my $sec=sprintf("%02d",$filegmtdate->sec());
my $gmt_timestamp = (join("-",($year,$month,$mday)) . "T" . join(":",($hour,$min,$sec)) . ".000Z"); # i.e. 2022-06-17T16:28:54.000Z
dprint ($i++,"[gmt_timestamp=$gmt_timestamp]\n");

#
# Create the Draw.io file with imported PlantUML code and SVG
# XML Data Template pulled from a random source file
#
my $drawio_xmldata = ('<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="' . $gmt_timestamp . '" agent="' . $DIO_AGENT_NAME . '" etag="' . $DIO_ETAG_ID . '" version="20.0.1" type="embed">
  <diagram id="' . $DIO_DIAGRAM_ID . '" name="Page-1">
    <mxGraphModel dx="1219" dy="1005" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <UserObject label="" plantUmlData="{&#xa;  &quot;data&quot;: &quot;' . $plantuml_escapedtextdata . '&quot;,&#xa;  &quot;format&quot;: &quot;svg&quot;&#xa;}" id="' . $DIO_USEROBJECT_ID . '">
          <mxCell style="shape=image;noLabel=1;verticalAlign=top;aspect=fixed;imageAspect=0;image=data:image/svg+xml,' . $plantuml_svgb64data . ';" parent="1" vertex="1">
            <mxGeometry x="0" y="0" width="' . $width . '" height="' . $height . '" as="geometry" />
          </mxCell>
        </UserObject>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>');

#
# Print the Draw.io file to STDOUT
#
print $drawio_xmldata;

__END__
