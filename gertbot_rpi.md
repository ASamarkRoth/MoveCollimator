Intro to gertbot-r-pi setup
===========================

[Intro](https://www.rs-online.com/designspark/an-introduction-to-the-gertbot)

As stated here: [gertbot.com](https://www.gertbot.com/) It runs with Linux and Windows. However as stated here: [raspbian](http://www.raspbian.org/) the OS raspbian is somewhat optimised software-wise for raspberry pi applications.

Power supply: Genesys, TDK-Lambda (Pizza box)

*   The stepper motor 17H261-02S/D requires 1.8 A, max (see mail _Compotech_). From the specification sheet of the motor it says R = 4 (+- 10%) Ohm. The stepper motor runs on DC. However from one of the _Compotech_ sheets they provide: " Pull out torque-speed curves 24 V DC Chopper driver, 2 phases". 

	* <http://compotech.se/blogg/2014/06/sa-valjer-du-ratt-spanning-din-stegmotordrift/>
	* <http://www.galilmc.com/download/application-note/note5466.pdf>
	* 1.2 A/phase and 4 Ohms wire-resistance -> 4.8 V (this is now slow) ~ 6V (1.5 A).
	* Now need a series resistor drive the controller which requires 8V.
	* What about connection of 2 stepper motors from the same power supply?

-   We have manual in-house.
-   Need RS232-USB connector cable from TDK-Lambda to r-pi.

	- Seems like it can work with a pure ethernet connector. RS232 is only a port for a "command protocol". BUT this needs verification ...

    -   [Dustin](https://www.dustinhome.se/product/5010778662/adapter?ssel=false&utm_campaign=pricerunner&utm_source=pricerunner.se&utm_medium=pricecompare&utm_content=5637146061)
-   There is a set communication protocol which can be used via a port

    -   interface: Python with pySerial module - [pySerial](http://www.varesano.net/blog/fabio/serial%20rs232%20connections%20python)
    * <http://stackoverflow.com/questions/676172/full-examples-of-using-pyserial-package>

Cableing:

-   There are cables that can be used for free in the µ-hall
-   How these are compatible with the power supply is still unclear!

