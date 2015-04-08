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



function handleFiles(editor,file){

            var filename = file.name;
            $.ajax({
                type:'GET',
                data:{"filename":file.name, "FileType":"post_image"},
                url:'/generateuploadurl/',
                contentType:"application/json",
                dataType:"json",
				async:false,
                success: function(data){ 
                    if(data.UploadUrl){
                    /*  console.log("upload url successfully created for " + file.name + " file");*/
                        console.log(data.UploadUrl);
                        handleUpload(editor,data.UploadUrl, file, data.Filename);
                    }
                },
                error: function(data){ 
                    console.log("error occured while creating upload url for " + file.name + ' file');
                    console.log(data);
                    
                },
            });
        }           
function handleUpload(editor,UploadUrl, file, Filename){
    $.ajax({
        xhr:xhr_with_progress,
        url:UploadUrl,
        type:'PUT',
        data:file,
        cache:false,
        contentType:false,
        processData:false,
        success: function(data){
			var NewImageItem = document.createElement("li");
			NewImageItem.setAttribute("class","list-group-item");
			var ImageHyperlink = document.createElement("a");
			ImageHyperlink.setAttribute("href", "https://d77da31580fbc8944c00-52b01ccbcfe56047120eec75d9cb2cbd.ssl.cf6.rackcdn.com/" + Filename);
			ImageHyperlink.setAttribute("target", "_blank");
			var ImageHyperlinkText = document.createTextNode(file.name);
			ImageHyperlink.appendChild(ImageHyperlinkText);
			NewImageItem.appendChild(ImageHyperlink);
			document.getElementById("post-images-list").appendChild(NewImageItem);
			editor.execCommand('mceInsertContent', false,'<img src=\"https://d77da31580fbc8944c00-52b01ccbcfe56047120eec75d9cb2cbd.ssl.cf6.rackcdn.com/' + Filename + '\" class=\"post-images\" />', {skip_undo : 1});
            
            console.log( file.name + " successfully uploaded");
        },
        error: function(data){ 
            alert("error occured while uploading " + file.name );
            console.log(data);
        }
    }); 
}








function upload2rackDownloadFile(editor,file){
	$.ajax({
		type:'GET',
		data:{"filename":file.name, "FileType":"download_file"}, 
		url:'/generateuploadurl/', 
		contentType:"application/json", 
		dataType:"json", 
		success: function(data){ 
			if(data.UploadUrl){ 
				/*  console.log("upload url successfully created for " + file.name + " file");*/ 
				console.log(data.UploadUrl);
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
						// DownloadButton="<p id='download_file'>" + filename + "&nbsp; <a id='download_button' href=https://6f45f6c2646a5cc3b02e-5797bc788d9575a168411f50126db6ce.ssl.cf6.rackcdn.com/" + Filename + " >Download</a></p>";
						//console.log(DownloadButton);
						var NewDownloadItem = document.createElement("li");
						NewDownloadItem.setAttribute("class","list-group-item");
						var DownloadFileHyperlink = document.createElement("a");
						DownloadFileHyperlink.setAttribute("href", "https://6f45f6c2646a5cc3b02e-5797bc788d9575a168411f50126db6ce.ssl.cf6.rackcdn.com/" + Filename);
						DownloadFileHyperlink.setAttribute("target", "_blank");
						var DownloadFileHyperlinkText = document.createTextNode(file.name);
						DownloadFileHyperlink.appendChild(DownloadFileHyperlinkText);
						NewDownloadItem.appendChild(DownloadFileHyperlink);
						console.log(NewDownloadItem);
						document.getElementById("download-files-list").appendChild(NewDownloadItem);
						editor.execCommand('mceInsertContent', false,'<a href=\"https://d77da31580fbc8944c00-52b01ccbcfe56047120eec75d9cb2cbd.ssl.cf6.rackcdn.com/' + Filename + '\" class=\"download-file\">'+ file.name + '</a>', {skip_undo : 1});
                
						console.log( file.name + " successfully uploaded");
					},
					error: function(data){ 
						alert("error occured while uploading " + file.name );
						console.log(data);
					}
				}); 

			}
		},
		error: function(data){ 
			console.error("error occured while creating upload url for " + file.name + ' file');
			console.log(data);
		},
	});
}

