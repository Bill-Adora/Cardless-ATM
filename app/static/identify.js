$(function() {
  if (window.JpegCamera) {
    var camera; // Initialized at the end

    var take_snapshots = function(count) {
      var snapshot = camera.capture();

      if (JpegCamera.canvas_supported()) {
        snapshot.get_canvas(add_snapshot);
      }
      else {
        // <canvas> is not supported in this browser. We'll use anonymous
        // graphic instead.
        var image = document.createElement("img");
        image.src = "no_canvas_photo.jpg";
        setTimeout(function() {add_snapshot.call(snapshot, image)}, 1);
      }

      if (count > 1) {
        setTimeout(function() {take_snapshots(count - 1);}, 500);
      }
    };

    var add_snapshot = function(element) {
      $(element).data("snapshot", this).addClass("item");

      var $container = $("#snapshots").append(element);
      var $camera = $("#camera");
      var camera_ratio = $camera.innerWidth() / $camera.innerHeight();

      var height = $container.height()
      element.style.height = "" + height + "px";
      element.style.width = "" + Math.round(camera_ratio * height) + "px";

      var scroll = $container[0].scrollWidth - $container.innerWidth();

      $container.animate({
        scrollLeft: scroll
      }, 200);
    };

    var select_snapshot = function () {
      $(".item").removeClass("selected");
      var snapshot = $(this).addClass("selected").data("snapshot");
      $("#upload_snapshot, #api_url").show();
      snapshot.show();
      $("#show_stream").show();
    };

    var upload_snapshot = function() {
      $("#container").append("<p> Please wait, loading ... </p>");
      var api_url = "http://127.0.0.1:5000/upload";
      console.log(api_url)
      $("#container").append("<p> Running Face Recognition... </p>").delay(5000).fadeIn();
      $("#container").append("<p>Identifying...</p>").delay(5000).fadeIn();
      var snapshot = $(".item.selected").data("snapshot");
      console.log(snapshot);
      snapshot.upload({api_url: api_url}).done(upload_done).fail(upload_fail);
    };

    var upload_done = function(response) {
      $("#container").append("Success...");
      $("#upload_snapshot").prop("disabled", false);
      $("#loader").hide();
      $("#upload_status").html("Upload successful");
      $("#container").append("<p>Welcome "+response+"</p>").delay(20000).fadeIn();
      $("#upload_result").html("Done");
      setTimeout(location.replace("http://127.0.0.1:5000/login"), 40000);
      //location.replace("http://127.0.0.1:5000/login");
    };

    var upload_fail = function(code, error, response) {
      $("#upload_snapshot").prop("disabled", false);
      $("#loader").hide();
      $("#upload_status").html(
        "Upload failed with status " + code + " (" + error + ")");
      $("#upload_result").html(response);
    };

    var discard_snapshot = function() {
      var element = $(".item.selected").removeClass("item selected");

      var next = element.nextAll(".item").first();

      if (!next.size()) {
        next = element.prevAll(".item").first();
      }

      if (next.size()) {
        next.addClass("selected");
        next.data("snapshot").show();
      }
      else {
        hide_snapshot_controls();
      }

      element.data("snapshot").discard();

      element.hide("slow", function() {$(this).remove()});
    };

    var show_stream = function() {
      $(this).hide();
      $(".item").removeClass("selected");
      hide_snapshot_controls();
      clear_upload_data();
      camera.show_stream();
    };

    var hide_snapshot_controls = function() {
      $(", #upload_snapshot, #api_url").hide();
    };

    $("#take_snapshots").click(function() {take_snapshots();});
    $("#snapshots").on("click", ".item", select_snapshot);
    $("#upload_snapshot").click(upload_snapshot);

    var options = {
      swf_url: "../dist/jpeg_camera.swf"
    }

    camera = new JpegCamera("#camera", options).ready(function(info) {
      $("#take_snapshots").show();
    });
  }
});