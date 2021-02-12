$(document).ready(function(){
     $('.sidenav').sidenav({ edge: "right", draggable: true });
     $(':header').css("font-family","'Press Start 2P'", "cursive")
     $('.parallax').parallax();
     $('.carousel').carousel();
     $("#copyright").text(new Date().getFullYear());
  });