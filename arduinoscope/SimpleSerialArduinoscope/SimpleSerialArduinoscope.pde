// 2014 - 05 - 25 this is being modified by DJ
// I tried to do so by forking from his github code, but unfortunately he's changed it completely from this
// So I've simply taken this from the googlecode page and put it on the shared github repo for hydrospect.
// due acknowledgement is given to David Konsumer, thanks for writing this!

/*
  This is a basic serial arduinoscope.
  
  (c) 2009 David Konsumer <david.konsumer@gmail.com>
  
  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2.1 of the License, or (at your option) any later version.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General
  Public License along with this library; if not, write to the
  Free Software Foundation, Inc., 59 Temple Place, Suite 330,
  Boston, MA  02111-1307  USA
 */

/*

Serial data comes in, in the format

1 23 34 4 5 76
1 23 34 4 5 76
1 23 34 4 5 76
1 23 34 4 5 76

(space seperates pin=data, LF-seperated frame data)

*/

import arduinoscope.*;
import processing.serial.*;

// this example requires controlP5
// http://www.sojamo.de/libraries/controlP5/
import controlP5.*;

// how many scopes, you decide.
Oscilloscope[] scopes = new Oscilloscope[1];
Serial port;
ControlP5 controlP5;


PFont fontLarge;
PFont fontSmall;

int LINE_FEED=13; // 13 is ASCII for carriage return

int[] vals;
int[] dimv = new int[2];
int[] posv = new int[2];

// zoom-related variables..
// mx and my represent the zoom origin point.. the eye of the storm
float mx, my;
float mouseOffsetX = 0, mouseOffsetY = 0, mouseOffsetXprev = 0, mouseOffsetYprev = 0;
int mouseStartPositionX, mouseStartPositionY;

void setup() {
  size(800, 620, P2D);
  background(0);
  
  controlP5 = new ControlP5(this);
  
  // set these up under tools/create font, if they are not setup.
  fontLarge = loadFont("TrebuchetMS-20.vlw");
  fontSmall = loadFont("Uni0554-8.vlw");
  
  dimv[0] = width-130;
  // 130 margin for text
  dimv[1] = height/scopes.length;
  
  // setup vals from serial
  vals = new int[scopes.length];
  // println(scopes.length);
  
  for (int i=0;i<scopes.length;i++){
    posv[0]=0;
    posv[1]=dimv[1]*i;
       
    // the next variables are the default zoom origin...
    mx = posv[0] + dimv[0]/2;
    my = posv[1] + dimv[1]/2;

    // random color, that will look nice and be visible
    scopes[i] = new Oscilloscope(this, posv, dimv);
    scopes[i].setScaleX(1.0f);
    scopes[i].setScaleY(1.0f);
    scopes[i].setLine_color(color((int)random(255), (int)random(127)+127, 255));
    
    // hard-coding the ADC res and Vref at the start..
    scopes[i].setResolution(8192.0f);
    scopes[i].setMultiplier(3.3f);
    
    controlP5.addButton("pause",1,dimv[0]+10,posv[1]+10,32,20).setId(i);
    controlP5.addButton("logic",1,dimv[0]+52,posv[1]+10,29,20).setId(i+50);
    controlP5.addButton("save",1,dimv[0]+92,posv[1]+10,29,20).setId(i+100);
    
    // new controlp5 elements aadded by DJ. These relate to the ADC
    Textlabel label1, label2, label3;
    stroke(255, 255, 255);
    line(dimv[0] + 10, posv[1]+45, dimv[0] + 130, posv[1]+45);
    
    controlP5.addTextlabel("label1").setText("ADC STUFF...").setPosition(dimv[0]+10, posv[1]+50);
    controlP5.addButton("Set ADC RES",1,dimv[0]+10,posv[1]+70,70,20).setId(500);
    controlP5.addButton("Vref",1,dimv[0]+10,posv[1]+100,29,20).setId(501);
    
    Textfield ADCRes, Vref_value, ZoomLevelX, ZoomLevelY;
    ADCRes = controlP5.addTextfield("ADCRes")
    .setPosition(dimv[0]+90,posv[1]+70)
      .setSize(30, 20)
        .setFocus(false)
          .setColor(color(255, 255, 255))
            .setId(502)
              .setText(str(int(scopes[0].getResolution())))
                .setCaptionLabel("");
    Vref_value = controlP5.addTextfield("Vref_value")
    .setPosition(dimv[0]+90,posv[1]+100)
      .setSize(30, 20)
        .setFocus(false)
          .setColor(color(255, 255, 255))
            .setId(502)
              .setText(str((scopes[0].getMultiplier())))
                .setCaptionLabel("");
                
    // y-zoom
    controlP5.addTextlabel("label2").setText("Y-ZOOMING").setPosition(dimv[0]+10, posv[1]+135);
    controlP5.addButton("YZoom-",1,dimv[0]+10,posv[1]+150,35,20).setId(502);
    controlP5.addButton("YZoom+",1,dimv[0]+85,posv[1]+150,35,20).setId(503);
    controlP5.addButton("YCenter0",1,dimv[0]+10,posv[1]+180,50,20).setId(504);
    controlP5.addButton("YZoom0",1,dimv[0]+70,posv[1]+180,50,20).setId(505);
    
    ZoomLevelY = controlP5.addTextfield("ZoomLevelY")
    .setPosition(dimv[0]+50,posv[1]+150)
      .setSize(30, 20)
        .setFocus(false)
          .setColor(color(255, 255, 255))
            .setId(502)
              .setText(str(scopes[0].getScaleY()))
                .setCaptionLabel("");

    // x-zoom
    controlP5.addTextlabel("label3").setText("X-ZOOMING").setPosition(dimv[0]+10, posv[1]+215);
    controlP5.addButton("XZoom-",1,dimv[0]+10,posv[1]+230,35,20).setId(506);
    controlP5.addButton("XZoom+",1,dimv[0]+85,posv[1]+230,35,20).setId(507);
    controlP5.addButton("XCenter0",1,dimv[0]+10,posv[1]+260,50,20).setId(508);
    controlP5.addButton("XZoom0",1,dimv[0]+70,posv[1]+260,50,20).setId(509);
    
    ZoomLevelX = controlP5.addTextfield("ZoomLevelX")
    .setPosition(dimv[0]+50,posv[1]+230)
      .setSize(30, 20)
        .setFocus(false)
          .setColor(color(255, 255, 255))
            .setId(502)
              .setText(str(scopes[0].getScaleX()))
                .setCaptionLabel("");

  }
  
  // println(Serial.list());
  port = new Serial(this, Serial.list()[0], 115200);
  
  // clear and wait for linefeed
  port.clear();
  port.bufferUntil(LINE_FEED);
}

void draw()
{
  background(0);
  stroke(255, 255, 255);
  line(dimv[0], posv[1]+45, dimv[0] + 130, posv[1]+45);
  line(dimv[0], posv[1]+130, dimv[0] + 130, posv[1]+130);
  line(dimv[0], posv[1]+210, dimv[0] + 130, posv[1]+210);
  line(dimv[0], posv[1]+290, dimv[0] + 130, posv[1]+290);
  
  // int[] vals = getTestValuesSquare();
  // int[] vals = getTestValuesSin();
  
  for (int i=0;i<scopes.length;i++){
    // update and draw scopes
    
    scopes[i].addData(vals[i]);
    scopes[i].draw(mx, my, mouseOffsetX, mouseOffsetY);
    
    // conversion multiplier for voltage
    float multiplier = scopes[i].getMultiplier()/scopes[i].getResolution();
    // println(multiplier);
    
    // convert arduino vals to voltage
    // float minval = scopes[i].getMinval() * multiplier;
    // float maxval = scopes[i].getMaxval() * multiplier;
    int[] values = scopes[i].getValues(); 
    float pinval =  values[values.length-1] * multiplier;
    
    // add lines
    scopes[i].drawBounds();
    stroke(255);
    
    int[] pos = scopes[i].getPos();
    int[] dim = scopes[i].getDim();
    
    line(0, pos[1], width, pos[1]);
    
    // add labels
    fill(255);
    textFont(fontLarge);
    text(pinval, width-60, pos[1] + dim[1] - 10);
    
    textFont(fontSmall);
    // text("min: " + minval, dim[0] + 10, pos[1] + 40);
    // text("max: " + maxval, dim[0] + 10, pos[1] + 48);
    
    fill(scopes[i].getLine_color());
    text("pin: " + i, dim[0] + 10,pos[1] + dim[1] - 10);
  }
  
  // draw text seperator, based on first scope
  int[] dim = scopes[0].getDim();
  stroke(255);
  line(dim[0], 0, dim[0], height);
  
  // update buttons
  controlP5.draw();
  // update the values of variables in the controlP5 elements..
  controlP5.get(Textfield.class, "ZoomLevelY").setText(String.format("%.2f", scopes[0].getScaleY()));
  
}

// handles button clicks
void controlEvent(ControlEvent theEvent) {
  int id = theEvent.controller().id();
  
  // button families are in chunks of 50 to avoid collisions
  if (id < 50){
    scopes[id].setPause(!scopes[id].isPause());
  }else if (id < 100){
    scopes[id-50].setLogicMode(!scopes[id-50].isLogicMode());
  }else if(id < 150){
    String fname = year() + "" + month() + "" + day() +".csv";
    scopes[id-100].saveData(fname);
    println("Saved as "+fname);
  } else if (id == 500) {
      print("New ADC resolution is "); 
      scopes[0].setResolution(float(controlP5.get(Textfield.class, "ADCRes").getText()));
      println(scopes[0].getResolution());
  } else if (id == 501) {
     print("New Vref for the ADC is "); 
     // println(controlP5.get(Textfield.class, "Vref_value").getText());
     scopes[0].setMultiplier(float(controlP5.get(Textfield.class, "Vref_value").getText()));
     println(scopes[0].getMultiplier());
  } else if (id == 502) {
    scopes[0].setScaleY(scopes[0].getScaleY()/1.1);
  } else if (id == 503) {
    scopes[0].setScaleY(scopes[0].getScaleY()*1.1);
    if (scopes[0].getScaleY() >= 19) {
      scopes[0].setScaleY(19.0f);
    }
  } else if (id == 504) {
    mouseOffsetY = 0; mouseOffsetYprev = 0; 
  } else if (id == 505) {
    scopes[0].setScaleY(1.0f);
  } else if (id == 506) {
    // scopes[0].setPause(true);    // pausekar
    if (scopes[0].getScaleX() != 1.0f) {
      scopes[0].setScaleX(scopes[0].getScaleX()/1.1);
    }
    if (scopes[0].getScaleX() < 1.0f) {
      // failsafe in case it gets zoomed out too damn much..
     scopes[0].setScaleX(1.0f); 
    }
  } else if (id == 507) {
    scopes[0].setScaleX(scopes[0].getScaleX()*1.1);
  } else if (id == 508) {
    mouseOffsetX = 0; mouseOffsetXprev = 0; 
  } else if (id == 509) {
    scopes[0].setScaleX(1.0f);
  }
}

// handle serial data
void serialEvent(Serial p) { 
  String data = p.readStringUntil(LINE_FEED);
  if (data != null) {
    // print(data);
    vals[0] = int(parseFloat(data));
    // println(vals[0]);
  }
}


// for test data, you can comment, if not using
int d=0;
ControlTimer ct = new ControlTimer();


int[] getTestValuesSin(){
  int[] vals = new int[scopes.length];
  
  // this is test data
  if (d==45){
    d=0;
  }
  
  int sval = (int) abs(sin(d*2)*1023.0f);
  for (int i=0;i<scopes.length;i++){
    vals[i]=sval;
  }
  
  d++;
  
  return vals;
}

int oldtime;
int time;
boolean up=false;

int[] getTestValuesSquare(){
  int[] vals = new int[scopes.length];
  
  ct.setSpeedOfTime(25);
  oldtime=time;
  time = ct.second();  
  
  if (oldtime==time){
    up = !up;
  }
  
  for (int i=0;i<scopes.length;i++){
    if (up){
      vals[i]=1023;
    }else{
       vals[i]=0;
    }
  }
  
  return vals;
}

// an exciting little piece of code to get mouse position, and hopefully make a zoom and drag thing out of it
void mousePressed() {
    printMouseCoordinates();
  // deal with the left button (zoom)
  if (mouseButton == LEFT && mouseX < dimv[0]) {
    // mx = mouseX;  my = mouseY;
    mouseStartPositionY = mouseY - (int)mouseOffsetYprev; 
    
  // deal with the right button (zoom out)
  } else if (mouseButton == RIGHT && mouseX < dimv[0]) {
    // mx = mouseX;  my = mouseY;
    
  }  
}

void mouseDragged() {
  // mx = dimv[0] - mouseX;  my = dimv[1] - mouseY;
  mouseOffsetY = mouseY - mouseStartPositionY;
}

void mouseReleased() {
  // printMouseCoordinates();
  mouseOffsetYprev = mouseOffsetY;
}
void printMouseCoordinates() {
   println(mouseX + ", " + mouseY); 
}
