# HX711 for Raspbery Py
----
HX711 code credited to [tatobari](https://github.com/tatobari)'s [HX711.py](https://github.com/tatobari/hx711py).

I've only made a few modifications on the way the captured bits are processed and to support Two's Complement, which it didn't.

Instructions
------------

* Include this block in your docker compose file using:
  ```
  image: bh.cr/olamide_omolola/scales
  ```

* Calibrate the block using the following steps:
  * Take a known object whose weight you know and place it on the scale.
  * Read the scale value (a positive or negative value) and divide by the weight of that object in grams
  * Add the calibration value in the `Device Variables` section of the balena dashboard OR include it in the docker-compose file as below:
    ```
      scale:
        image: bh.cr/olamide_omolola/scales
        restart: always
        privileged: true
        labels:
          io.balena.features.kernel-modules: '1'
          io.balena.features.sysfs: '1'
          io.balena.features.supervisor-api: '1'
        environment: 
          - CALIBRATION_VALUE=-254.1

    ```


Using a 2-channel HX711 module
------------------------------
This block does not support a 2-channel HX711 module but the underlying library does. 
It is trivial to add the block support but I chose to keep the block small without unnecessary bloat.

For adding a 2-channel HX711 module, follow [tatobari](https://github.com/tatobari)'s instructions below: 

Channel A has selectable gain of 128 or 64.  Using set_gain(128) or set_gain(64)
selects channel A with the specified gain.

Using set_gain(32) selects channel B at the fixed gain of 32.  The tare_B(),
get_value_B() and get_weight_B() functions do this for you.

This info was obtained from an HX711 datasheet located at
https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf

