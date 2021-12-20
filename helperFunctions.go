package main

import (
	"bytes"
	"fmt"
	"log"
	"net"
	"os"
	"os/exec"
	"time"
)

// Handle err for helper functions
func errHandler(errorObject error, errorMessage string, toExit bool) {
	if errorObject != nil {
		fmt.Println(errorMessage)
		if toExit {
			os.Exit(1)
		}
	}
}

// Translate host into ip
func dnsLookup(machine string) []byte {
	cmd := exec.Command("/usr/bin/dig", "+short", machine)
	output, err := cmd.CombinedOutput()
	output = bytes.Trim(output, "\n")
	errHandler(err, "Couldn't lookup machine address:"+machine, true)
	return output
}

// Get Local IP
func getLocalIP() string {
	interfaceAddresses, err := net.InterfaceAddrs()
	if err != nil {
		return ""
	}
	for _, address := range interfaceAddresses {
		if ipNet, ok := address.(*net.IPNet); ok && !ipNet.IP.IsLoopback() {
			if ipNet.IP.To4() != nil {
				return ipNet.IP.String()
			}
		}
	}
	return ""
}

// Get the time stamp
func getTime() int {
	t := time.Now()
	return t.Hour()*3600 + t.Minute()*60 + t.Second()
}

func storeData(path string) {
	_, err := exec.Command("python3", "store_data.py", path).Output()
	if err != nil {
		log.Fatal("Error in executing Python script for storing data: "+path, err)
	}
}
