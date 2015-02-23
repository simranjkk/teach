//Code for Image upload

// Custom jQuery xhr instance to support our progress bar.

var xhr_with_progress = function() {
     var xhr = new XMLHttpRequest();
     xhr.upload.addEventListener("progress",
         function(evt) {
             if (!evt.lengthComputable) return;
             var percentComplete = evt.loaded / evt.total;
             $("#progress-bar div.progress-bar").css('width', String(100*percentComplete) + "%");
         }, false);
     return xhr;
 };





$.support.cors = true;//For cross origin transfer

//Event listners to avoid default drag and drop reaction of browser
window.addEventListener("dragover",function(e){
  e = e || event;
  e.preventDefault();
},false);
window.addEventListener("drop",function(e){
  e = e || event;
  e.preventDefault();
},false);


//Event listners to listen drag and drop image in box
var dropbox = document.getElementById("dropbox"); 
dropbox.addEventListener("dragover",function(e){
  e = e || event;
  e.preventDefault();
  $('#dropbox').css("background-color","gray");
},false);

window.addEventListener("dragleave",function(e){
  e = e || event;
  e.preventDefault();
  $('#dropbox').css("background-color","white"); 
},false);


dropbox.addEventListener("drop",drop,false);

function drop(evt){
    $('#dropbox').css("background-color","white"); 
    console.log("detected");
    evt.stopPropagation();
    evt.preventDefault();
 
    var files = evt.dataTransfer.files;
    var count = files.length;
    if(count>0){
        for(var i=0;i<count;i++){
            handleFiles(files[i]);
        }
    }
}


function handleFiles(file){

            var filename = file.name;
            $.ajax({
                type:'GET',
                data:{"filename":file.name, "FileType":"post_image"},
                url:'/generateuploadurl/',
                contentType:"application/json",
                dataType:"json",
                success: function(data){ 
                    if(data.UploadUrl){
                    /*  console.log("upload url successfully created for " + file.name + " file");*/
                        console.log(data.UploadUrl);
                        handleUpload(data.UploadUrl, file, data.Filename);
                    }
                },
                error: function(data){ 
                    console.log("error occured while creating upload url for " + file.name + ' file');
                    console.log(data);
                    
                },
            });
        }           
function handleUpload(UploadUrl, file, Filename){
    $.ajax({
        xhr:xhr_with_progress,
        url:UploadUrl,
        type:'PUT',
        data:file,
        cache:false,
        contentType:false,
        processData:false,
        success: function(data){
            image="<img class='post-images' src=https://d77da31580fbc8944c00-52b01ccbcfe56047120eec75d9cb2cbd.ssl.cf6.rackcdn.com/" + Filename + ">";
            console.log(image);
            $('iframe').contents().find('body.cke_editable').contents().append(image);
            
            console.log( file.name + " successfully uploaded");
        },
        error: function(data){ 
            console.log("error occured while uploading " + file.name );
            console.log(data);
        }
    }); 
}








$("#downloadfile").on("change",function(e){ 
                        var file=this.files[0];
                        var filename = file.name;
                        $.ajax({
                            type:'GET',
                            data:{"filename":file.name, "FileType":"download_file"}, url:'/generateuploadurl/', contentType:"application/json", dataType:"json", success: function(data){ if(data.UploadUrl){ /*  console.log("upload url successfully created for " + file.name + " file");*/ console.log(data.UploadUrl);
                                    Filename = data.Filename;
                                    $.ajax({
                                        xhr:xhr_with_progress,
                                        url:data.UploadUrl,
                                        type:'PUT',
                                        data:file,
                                        cache:false,
                                        contentType:false,
                                        processData:false,
                                        success: function(data){
                                            DownloadButton="<div class='row' ><div class='col-md-offset-5'><a id='download_button' class='btn btn-default' type='button' href=https://6f45f6c2646a5cc3b02e-5797bc788d9575a168411f50126db6ce.ssl.cf6.rackcdn.com/" + Filename + " download>Download</a></div></div>";
                                            console.log(DownloadButton);
                                            $('iframe').contents().find('body.cke_editable').contents().append(DownloadButton);
                
                                             console.log( file.name + " successfully uploaded");
                                        },
                                        error: function(data){ 
                                            console.log("error occured while uploading " + file.name );
                                            console.log(data);
                                        }
                                    }); 

                                }
                            },
                            error: function(data){ 
                                console.log("error occured while creating upload url for " + file.name + ' file');
                                console.log(data);
                            },
                        });




});

