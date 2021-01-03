import os
import genanki
import toga
from screen_state import ScreenWithState

RANDOMIZATION_SCRIPT = """
<script>
!function(f,a,c){var s,l=256,p="random",d=c.pow(l,6),g=c.pow(2,52),y=2*g,h=l-1;function n(n,t,r){function e(){for(var n=u.g(6),t=d,r=0;n<g;)n=(n+r)*l,t*=l,r=u.g(1);for(;y<=n;)n/=2,t/=2,r>>>=1;return(n+r)/t}var o=[],i=j(function n(t,r){var e,o=[],i=typeof t;if(r&&"object"==i)for(e in t)try{o.push(n(t[e],r-1))}catch(n){}return o.length?o:"string"==i?t:t+"\0"}((t=1==t?{entropy:!0}:t||{}).entropy?[n,S(a)]:null==n?function(){try{var n;return s&&(n=s.randomBytes)?n=n(l):(n=new Uint8Array(l),(f.crypto||f.msCrypto).getRandomValues(n)),S(n)}catch(n){var t=f.navigator,r=t&&t.plugins;return[+new Date,f,r,f.screen,S(a)]}}():n,3),o),u=new m(o);return e.int32=function(){return 0|u.g(4)},e.quick=function(){return u.g(4)/4294967296},e.double=e,j(S(u.S),a),(t.pass||r||function(n,t,r,e){return e&&(e.S&&v(e,u),n.state=function(){return v(u,{})}),r?(c[p]=n,t):n})(e,i,"global"in t?t.global:this==c,t.state)}function m(n){var t,r=n.length,u=this,e=0,o=u.i=u.j=0,i=u.S=[];for(r||(n=[r++]);e<l;)i[e]=e++;for(e=0;e<l;e++)i[e]=i[o=h&o+n[e%r]+(t=i[e])],i[o]=t;(u.g=function(n){for(var t,r=0,e=u.i,o=u.j,i=u.S;n--;)t=i[e=h&e+1],r=r*l+i[h&(i[e]=i[o=h&o+t])+(i[o]=t)];return u.i=e,u.j=o,r})(l)}function v(n,t){return t.i=n.i,t.j=n.j,t.S=n.S.slice(),t}function j(n,t){for(var r,e=n+"",o=0;o<e.length;)t[h&o]=h&(r^=19*t[h&o])+e.charCodeAt(o++);return S(t)}function S(n){return String.fromCharCode.apply(0,n)}if(j(c.random(),a),"object"==typeof module&&module.exports){module.exports=n;try{s=require("crypto")}catch(n){}}else"function"==typeof define&&define.amd?define(function(){return n}):c["seed"+p]=n}("undefined"!=typeof self?self:this,[],Math);

var seed_hourly = Math.floor(Date.now() / 1000 / 3600);
var randy = new Math.seedrandom(seed_hourly);

// both included [min, max]
function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(randy() * (max - min + 1)) + min;
}

var rand_int = getRandomInt(0, 4);
var elem = document.getElementById("sent-" + rand_int);

elem.style.display = "block";

</script>
"""

class CardScreen(ScreenWithState):
    def construct_gui(self):
        return toga.Box(children=[toga.Label("Creating cards or so")])

    def update_gui_contents(self):
        multisentence_model = genanki.Model(
            1607392319,
            "Simple Model",
            fields=[{"name": "sentence"}, {"name": "definition"},],
            templates=[
                {
                    "name": "One-To-Many Cards",
                    "qfmt": "{{sentence}}" + RANDOMIZATION_SCRIPT,
                    "afmt": '{{FrontSide}}<hr id="answer">{{definition}}',
                }
            ],
        )

        epub_path = self._state["epub_path"]
        deck_name = os.path.basename(epub_path)
        book_deck = genanki.Deck(2059400110, deck_name)

        for card in self._state["card_models"]:
            field_sentence = ""
            field_definition = card["definition"]
                
            for isent, sent in enumerate(card["sentences"]):
                field_sentence += f"<div id='sent-{isent}' style='display:none;'>{sent}</div>"

            note_basic = genanki.Note(
                model=multisentence_model, fields=[field_sentence, field_definition]
            )
            book_deck.add_note(note_basic)

        genanki.Package(book_deck).write_to_file("output.apkg")

