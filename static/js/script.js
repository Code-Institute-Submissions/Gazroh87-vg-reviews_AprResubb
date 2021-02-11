$(document).ready(function(){
     $('.sidenav').sidenav({ edge: "right", draggable: true });
     $("#copyright").text(new Date().getFullYear());
  });