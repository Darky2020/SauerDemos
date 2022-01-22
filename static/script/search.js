var firstgameid = 0;
var lastgameid = 9999999999;

const removeChilds = (parent) => {
    while (parent.lastChild) {
        parent.removeChild(parent.lastChild);
    }
};

function resetgameid()
{
	firstgameid = 0;
	lastgameid = 9999999999;
}

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



function SearchGames(getNext, isSearch) {
	if(isSearch)
    {
    	resetgameid();
    }
	var url = "/api/demos/find?limit=10"

	var servaddr = document.getElementById('servaddr').value;
	var mapname = document.getElementById('mapname').value;
	var gamemode = document.getElementById('gamemode').value;
	var gametype = document.getElementById('gametype').value;
	var beforetime = document.getElementById('beforetime').value;
	var aftertime = document.getElementById('aftertime').value;

	if(servaddr)
	{
		url += "&host=" + servaddr.split(":")[0] + "&port=" + servaddr.split(":")[1]; 
	}

	if(mapname)
	{
		url += "&mapname=" + mapname;
	}

	if(gamemode != "None")
	{
		url += "&gamemode=" + gamemode;
	}

	if(gametype != "None")
	{
		console.log(gametype);
		url += "&gametype=" + gametype;
	}

	if(beforetime)
	{
		url += "&beforetimestamp=" + beforetime;
	}

	if(aftertime)
	{
		url += "&aftertimestamp=" + aftertime;
	}

	if(getNext)
	{
		url += "&beforeid=" + lastgameid;
	}
	else
	{
		url += "&afterid=" + firstgameid;
	}

	fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Request failed with status ${reponse.status}`)
            }
            return response.json()
        })
        .then(data => {
            var result = data["data"]["result"];
            if(result.length > 0 || isSearch)
            {
            	removeChilds(document.getElementById('info-table'));
            }

            	if(!getNext)
            	{
            		result = result.reverse();
            	}
  
            	for (let i = 0; i < result.length; i++) {
            		if(i==0)
            		{
            			firstgameid = parseInt(result[0]["gameid"]);
            		}
                	AddToTable(result[i]);
           		}
  
        })
        .catch(error => console.log(error))
}

SearchGames(true, true)