# Formats of communication

## sd Charging Communication

### Current battery percentage from Car to Charger:
Topic: `ttm4115/g11/chargers/<charger_id>`
```
{
  "command": "battery_percentage",
  "percentage": <percentage>
}
```

### Stop charging from Charger to Car:
Topic: `ttm4115/g11/cars/<car_id>`
```
{
  "command": "stop_charging"
}
```

## sd Charging for User
### "Request Activation and Make Charging unit unavailable":
`HTTP POST REQUEST, coming soon`
```
{
  "charger_id": <id of charger>,
  "car_id": <id of car>,
  "battery_target": <target percentage of car battery>,
}
```

### "OK":
HTTP 200 OK response

### "Allow charging" from Server to Charger:
Topic: `ttm4115/g11/chargers/<charger-id>`
```
{
  "command": "allow_charging",
  "battery_target": <target percentage of car battery>
}
```

### "Car is charged" from Charger to Server:
HTTP, COMMING SOON
```
{
  "command": "car_charged",
  "car_id": <id of car>,
  "charger_id": <id of charger>
}
```

### "Car is charged" from Server to App:
Might be unneccessary, when the charger tells the server it is finished and the user updates its UI, the user will know.

### "Station available" Charger to Server:
HTTP REQUEST, COMMMING SOON
```
{
  "command": "charger_available"
}
```

The rest will be HTTP, updating soon
## sd Overview
### "req_overview_page" App to Server:
_Could be HTTP later_
```
{
  "command": "req_overview_page"
}
```

### "req_overview_page" Server to App:
_Could be HTTP later_
```
{
  "command": "send_overview_page",
  "data": <charger data e.g. unavailable? reserved? etc.>
}
```

### "req_charging_unit_info" App to Server:
_Could be HTTP later_
```
{
  "command": "req_charging_unit_info"
}
```

### "send_charging_unit_info" Server to App:
_Could be HTTP later_
```
{
  "command": "send_charging_unit_info",
  "charger_id": <id of charger>
  "data": <request charging unit info (more detailed)>,
}
```

## sd Reservation
### "Request reservation slots" from App to Server:
_Could be HTTP later_
```
{
  "command": "get_reservable_slots",
  "start_time": <start time of reservation>,
  "end_time": <end time of reseervation>
}
```

### "Return reservation slots" from App to Server:
_Could be HTTP later_
```
{
  "command": "response",
  "response_class": <"ERROR" or "OK">,
  "reservation_slots": <list of available reservation slots>
}
```

### "Save reservation" from App to Server:
_Could be HTTP later_
```
{
  "command": "post_reservation",
  "charger_id": <id of charger>,
  "car_id": <id of car>
}
```

### "Return reservation success" from App to Server:
_Could be HTTP later_
```
{
  "command": "response",
  "response_class": <"ERROR" or "OK">,
}
```
