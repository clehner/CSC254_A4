window.onload = hash_change;
window.onhashchange = hash_change;

var current = '';

function hash_change(){
	hash = location.hash.substr(1);
	section = document.getElementById(hash);
	if(hash && section) {
		section.parentNode.className = 'highlight';

		if(current)
			current.className = "";
		current = section.parentNode;
	}

}
