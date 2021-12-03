package main

import (
	"bufio"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"sync"
	"time"

	_ "github.com/go-sql-driver/mysql"
)

type Daemon struct {
	ID        string
	IPAddress string
	Port      string
}

type Message struct {
	ID      string
	Type    string
	Payload string
}

var masterAddr = "128.174.246.108:3000"
var isMaster = false
var workerTimeStamp = map[string]int{}
var workerStatus = map[string]bool{}
var currentTask = map[string]string{}
var working = false
var idToServerName = map[string]string{"172.22.224.119": "Owl2", "128.174.246.108": "Falcon", "172.22.224.10": "Owl", "172.22.224.120": "Owl3"}
var mutex = &sync.Mutex{}

// todo 1:
// change username, pw, host, and dbname
// db, err := sql.Open("mysql", "<username>:<pw>@tcp(<host>:<port>)/<dbname>")
var db, _ = sql.Open("mysql", "bm12:publications123@tcp(Owl2.cs.illinois.edu:3306)/bm12_publications")

func (daemon Daemon) receiver() {
	servaddr, err := net.ResolveUDPAddr("udp", ":"+daemon.Port)
	serv, err := net.ListenUDP("udp", servaddr)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer serv.Close()
	buf := make([]byte, 1024)
	fmt.Println("Receiver is ready!")

	for {
		n, _, err := serv.ReadFromUDP(buf)
		if err != nil {
			fmt.Println(err)
			return
		}
		var message Message
		err = json.Unmarshal(buf[:n], &message)
		if err != nil {
			fmt.Println(err)
			return
		}
		if message.Type == "HEARTBEAT" && isMaster {
			mutex.Lock()
			workerTimeStamp[message.ID] = getTime()
			if message.Payload == "working" {
				workerStatus[message.ID] = true
			} else {
				workerStatus[message.ID] = false
			}
			mutex.Unlock()
		}
		if message.Type == "TASK" {
			working = true
			fmt.Println("Start working on: " + message.Payload)

			// todo 2:
			// change the following code to run your script
			// instructions for tasks will be stored in "message.Payload" (see "todo 3")
			_, err := exec.Command("python", "script.py", message.Payload).Output()
			if err != nil {
				log.Fatal("Error in executing Python script for : " + message.Payload)
			}

			fmt.Println("Finished " + message.Payload + "\n")
			working = false
		}
	}
}

func (daemon Daemon) sender(addr string, messageType string, payload string) {
	s, err := net.ResolveUDPAddr("udp4", addr)
	c, err := net.DialUDP("udp4", nil, s)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer c.Close()
	message := Message{ID: daemon.ID, Type: messageType, Payload: payload}
	m, err := json.Marshal(message)
	_, err = c.Write(m)
	if err != nil {
		fmt.Println(1, err)
		return
	}
}

func convertIdToServerName(id string) string {
	s := strings.Split(id, ":")
	return idToServerName[s[0]]
}

func (daemon Daemon) heartbeatManager() {
	for {
		if isMaster {
			currentTime := getTime()
			mutex.Lock()
			for k, _ := range workerStatus {
				if currentTime-workerTimeStamp[k] > 10 {

					// todo 4
					// handle worker failure
					// when the master detects worker failures, the following code will be executed on the master side
					log.Println(convertIdToServerName(k), "fails on task:", currentTask[k])

					delete(workerStatus, k)
					delete(workerTimeStamp, k)
					delete(currentTask, k)
				}
			}
			mutex.Unlock()
		} else {
			var m = "not working"
			if working {
				m = "working"
			}
			go daemon.sender(masterAddr, "HEARTBEAT", m)
		}
		time.Sleep(1 * time.Second)
	}
}

func (daemon Daemon) taskScheduler() {
	for {
		mutex.Lock()
		for k, v := range workerStatus {
			if !v {

				// todo 3:
				// read a task from the table "Tasks"
				// change this code to read a task from your list of tasks
				var p int
				_ = db.QueryRow("select min(priority) from Tasks").Scan(&p)
				var task string
				err := db.QueryRow("select task from Tasks where priority = ?", strconv.Itoa(p)).Scan(&task)
				if err != nil {
					fmt.Println(err)
				}
				_ = db.QueryRow("update Tasks set priority = 2147483647 where task = ?", task).Scan()

				go daemon.sender(k, "TASK", task)
				currentTask[k] = task
				log.Println("Assign task", task, "to", convertIdToServerName(k))
			}
		}
		mutex.Unlock()
		time.Sleep(time.Second)
	}
}

func main() {
	// verify that MySQL is connected
	db.Ping()
	arguments := os.Args
	if len(arguments) == 1 {
		fmt.Println("Please provide a host:port string")
		return
	}
	var daemon = new(Daemon)
	daemon.Port = os.Args[1]
	daemon.IPAddress = getLocalIP()
	daemon.ID = daemon.IPAddress + ":" + daemon.Port

	if daemon.ID == masterAddr {
		fmt.Println("This is Master!")
		isMaster = true
	}
	go daemon.heartbeatManager()
	go daemon.receiver()
	fmt.Printf("Port:%s, IP: %s\n", daemon.Port, daemon.IPAddress)

	if isMaster {
		go daemon.taskScheduler()
	}

	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		if scanner.Text() == "ls" {
			for k, v := range currentTask {
				fmt.Println(convertIdToServerName(k), "is working on", v)
			}
		}
	}
}
