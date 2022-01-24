var lastgameid = 9999999999;

function formatTime(delta)
{
    if (delta < 60) {
        return delta.toString() + " seconds ago";
    }
    if (delta < 3600) {
        return Math.floor(delta/60).toString() + " minutes ago";
    }
    if (delta < 86400) {
        return Math.floor(delta/3600).toString() + " hours ago";
    }
    if (delta < 604800) {
        return Math.floor(delta/86400).toString() + " days ago";
    }
    if (delta < 2629743) {
        return Math.floor(delta/604800).toString() + " weeks ago";
    }
    if (delta < 31556926) {
        return Math.floor(delta/2629743).toString() + " months ago";
    }
    return Math.floor(delta/31556926).toString() + " years ago";
}

function AddToTable(info) {
    var tbody = document.getElementById('info-table');
    var row = document.createElement("tr");

    var cell = document.createElement("td");
    var cellText = document.createTextNode(info["gameid"]);
    cell.appendChild(cellText);
    row.appendChild(cell);

    var cell = document.createElement("td");
    var cellText = document.createTextNode(info["gamemode"]);
    cell.appendChild(cellText);
    row.appendChild(cell);

    cell = document.createElement("td");
    cellText = document.createTextNode(info["gametype"]);
    cell.appendChild(cellText);
    row.appendChild(cell);

    cell = document.createElement("td");
    cellText = document.createTextNode(info["mapname"]);
    cell.appendChild(cellText);
    row.appendChild(cell);

    cell = document.createElement("td");
    cellText = document.createTextNode(info["serverdesc"]);
    cell.appendChild(cellText);
    row.appendChild(cell);

    cell = document.createElement("td");
    cellText = document.createTextNode((info["host"] + ":" + info["port"]));
    cell.appendChild(cellText);
    row.appendChild(cell);

    cell = document.createElement("td");
    cellText = document.createElement("a");
    cellText.text = "Download";
    cellText.href = info["download_link"];
    cell.appendChild(cellText);
    row.appendChild(cell);

    cell = document.createElement("td");
    cellText = document.createElement("a");
    cellText.text = "Sauertracker";
    cellText.href = info["sauertracker_link"];
    cell.appendChild(cellText);
    row.appendChild(cell);

    cell = document.createElement("td");
    cellText = document.createTextNode(formatTime(Math.floor(Date.now()/1000) - info["timestamp"]));
    cell.appendChild(cellText);
    row.appendChild(cell);

    tbody.appendChild(row);

    lastgameid = info["gameid"];
}

function LoadGames() {
    fetch("/api/demos/find?limit=20&beforeid=" + (lastgameid.toString()))
        .then(response => {
            if (!response.ok) {
                throw new Error(`Request failed with status ${reponse.status}`)
            }
            return response.json()
        })
        .then(data => {
            var arr = data["data"]["result"];
            for (let i = 0; i < arr.length; i++) {
                AddToTable(arr[i]);
            }
        })
        .catch(error => console.log(error))
}

LoadGames()