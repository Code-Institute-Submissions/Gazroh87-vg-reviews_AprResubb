$(document).ready(function () {
    $('.sidenav').sidenav({ edge: "right", draggable: true });
    $(':header').css("font-family", "'Press Start 2P'", "cursive")
    $('.parallax').parallax();
    $('.carousel').carousel();
    $('.collapsible.expandable').collapsible({ accordion: false });
    $('select').formSelect();
    $(".datepicker").datepicker();
    $("#copyright").text(new Date().getFullYear());
});