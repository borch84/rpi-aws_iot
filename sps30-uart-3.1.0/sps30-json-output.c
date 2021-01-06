/*
 * Copyright (c) 2018, Sensirion AG
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * * Redistributions of source code must retain the above copyright notice, this
 *   list of conditions and the following disclaimer.
 *
 * * Redistributions in binary form must reproduce the above copyright notice,
 *   this list of conditions and the following disclaimer in the documentation
 *   and/or other materials provided with the distribution.
 *
 * * Neither the name of Sensirion AG nor the names of its
 *   contributors may be used to endorse or promote products derived from
 *   this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#include <stdio.h>  // printf
#include <stdlib.h> //exit()
#include "sensirion_uart.h"
#include "sps30.h"
#include <string.h>

/**
 * TO USE CONSOLE OUTPUT (PRINTF) AND WAIT (SLEEP) PLEASE ADAPT THEM TO YOUR
 * PLATFORM
 */
//#define printf(...)

int main(int argc, char  *argv [ ]) {
    FILE *fp;
    char json_output_file[] = "/home/pi/aws_iot/sps30-uart-3.1.0/sps30.json"; //Default Value
    if (argc == 2) {
        strcpy(json_output_file, argv[1]);
    }

    fp = fopen(json_output_file,"w");
    if (fp == NULL) {
       printf("file can't be opened\n");
       exit(1);
    }


    struct sps30_measurement m;
    char serial[SPS30_MAX_SERIAL_LEN];
    const uint8_t AUTO_CLEAN_DAYS = 4;
    int16_t ret;

    while (sensirion_uart_open() != 0) {
        printf("UART init failed\n");
        fprintf(fp,"{\"error\":\"UART_INIT_FAILED\"}");
        sensirion_sleep_usec(1000000); /* sleep for 1s */
    }
    fp=freopen(NULL,"w",fp);

    /* Busy loop for initialization, because the main loop does not work without
     * a sensor.
     */
    while (sps30_probe() != 0) {
        printf("SPS30 sensor probing failed\n");
        fprintf(fp,"{\"error\":\"PROBING_FAILED\"}");
        sensirion_sleep_usec(1000000); /* sleep for 1s */
        fp=freopen(NULL,"w",fp);
    }
    printf("SPS30 sensor probing successful\n");

    ret = sps30_get_serial(serial);
    if (ret) {
        printf("error %d reading serial\n", ret);
        fprintf(fp,"{\"error\":\"error %d reading serial\"}",ret);
        fclose(fp);
        exit(1);
    } else {
        printf("SPS30 Serial: %s\n", serial);
    }
    fp=freopen(NULL,"w",fp);
    ret = sps30_set_fan_auto_cleaning_interval_days(AUTO_CLEAN_DAYS);
    if (ret) {
        printf("error %d setting the auto-clean interval\n", ret);
        fprintf(fp,"{\"error\":\"error %d setting the auto-clean interval\"}",ret);
        fclose(fp);
        exit(1);
    }
    ret = sps30_start_measurement();
    if (ret < 0) {
        printf("error starting measurement\n");
        fprintf(fp,"{\"error\":\"error starting measurement\"}");
        fclose(fp);
        exit(1);
    }

    printf("measurements started\n");
    fclose(fp);

    //do {
        //fp=freopen(NULL,"w",fp); //reopen el file limpia el contenido
        fp = fopen(json_output_file,"w");
        if (fp == NULL) {
       	 printf("file can't be opened\n");
       	 exit(1);
        }

        ret = sps30_read_measurement(&m);
        if (ret < 0) {
            printf("error reading measurement\n");
            //No impreme errores en el archivo sps30.json
            //fprintf(fp,"{\"error\":\"error reading measurement\"}");
            fclose(fp); //cierra el archivo sps30.json
        } else {
	        fprintf(fp,"{");
            int16_t chipState = SPS30_IS_ERR_STATE(ret);
	        if (chipState) {
                //printf("Chip state: %u - measurements may not be accurate\n",SPS30_GET_ERR_STATE(ret));
                printf("Chip state: %u - measurements may not be accurate\n",chipState);
		        //fprintf(fp,"\"error\":\"CHPST%u\",",chipState);
            }

            printf("serial: %s\n"
		   "auto_clean_interval_days: %u\n"
		   "measured values:\n"
                   "\t%0.2f pm1.0\n"
                   "\t%0.2f pm2.5\n"
                   "\t%0.2f pm4.0\n"
                   "\t%0.2f pm10.0\n"
                   "\t%0.2f nc0.5\n"
                   "\t%0.2f nc1.0\n"
                   "\t%0.2f nc2.5\n"
                   "\t%0.2f nc4.5\n"
                   "\t%0.2f nc10.0\n"
                   "\t%0.2f typical particle size\n\n",
                   serial, AUTO_CLEAN_DAYS, m.mc_1p0, m.mc_2p5, m.mc_4p0, m.mc_10p0, m.nc_0p5, m.nc_1p0,
                   m.nc_2p5, m.nc_4p0, m.nc_10p0, m.typical_particle_size);
        
	        fprintf(fp, "\"serial\":\"%s\","
		       "\"auto_clean_interval_days\":%d,"
		       "\"pm1.0\":%0.2f,"
                       "\"pm2.5\":%0.2f,"
                       "\"pm4.0\":%0.2f,"
                       "\"pm10.0\":%0.2f,"
                       "\"nc0.5\":%0.2f,"
                       "\"nc1.0\":%0.2f,"
                       "\"nc2.5\":%0.2f,"
                       "\"nc4.5\":%0.2f,"
                       "\"nc10.0\":%0.2f,"
                       "\"tps\":%0.2f}",
		    serial, AUTO_CLEAN_DAYS, m.mc_1p0, m.mc_2p5, m.mc_4p0, m.mc_10p0, m.nc_0p5, m.nc_1p0,
                       m.nc_2p5, m.nc_4p0, m.nc_10p0, m.typical_particle_size); 
	        fclose(fp);
	        //sensirion_sleep_usec(120000000); /* sleep for 120s */
	    }

    //} while (1);

    /*

    sensirion_uart_close() no esta definido en el archivo sensirion_uart_implementation.c para raspberry.

    if (sensirion_uart_close() != 0)
        printf("failed to close UART\n");

    */


    return 0;
}
