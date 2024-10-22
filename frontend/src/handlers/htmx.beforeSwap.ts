import copy from "copy-to-clipboard";
import { Toast, ToastLevel } from "../components/toast";

async function toastifyResponse(evt: CustomEvent) {
  const status = evt.detail.xhr.status;
  const toast = document.querySelector("c-toast") as Toast;

  let responseMessage;
  let toastLevel = ToastLevel.SUCCESS;
  try {
    responseMessage = JSON.parse(evt.detail.serverResponse)["detail"];
  } catch {
    responseMessage = evt.detail.serverResponse;
  }

  if (status >= 200 && status < 300) {
    if (status === 201 && responseMessage["shortened_url"]) {
      const copied = copy(responseMessage.shortened_url);
      if (copied) {
        responseMessage = `Short URL ${responseMessage.shortened_url} created and copied to clipboard!`;
      } else {
        responseMessage = `Short URL ${responseMessage.shortened_url} created succesfully!`;
      }
    }
  } else if (status >= 400 && status < 500) {
    toastLevel = ToastLevel.WARNING;
  } else if (status >= 500) {
    toastLevel = ToastLevel.ERROR;
    responseMessage = "Something went wrong, please try again later.";
  }
  toast.show(responseMessage, toastLevel);
}

document.addEventListener("htmx:beforeSwap", toastifyResponse);
