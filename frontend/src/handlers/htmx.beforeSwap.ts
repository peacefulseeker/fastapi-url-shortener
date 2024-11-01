import { Toast, ToastLevel } from "../components/toast";
import { ShortenedUrlResponse } from "../types";
import copy from "copy-to-clipboard";

function processUrlShortened(responseMessage: ShortenedUrlResponse, toast: Toast) {
  const copied = copy(responseMessage.shortened_url);
  let toastMessage = `Short URL <pre class="break-all text-sm font-bold whitespace-pre-wrap">${responseMessage.shortened_url}</pre> created`;
  if (copied) {
    toastMessage += `and copied to clipboard!`;
    if (responseMessage.expires_at) {
      const expiresAt = new Date(responseMessage.expires_at * 1000).toLocaleString();
      toastMessage += `<br />With expiration date set to ${expiresAt}`;
    }
  } else {
    toastMessage = `Short URL <pre class="break-all text-sm font-bold whitespace-pre-wrap">${responseMessage.shortened_url}</pre> created succesfully!`;
  }
  toast.show(toastMessage, ToastLevel.SUCCESS, null);
}

function toastifyResponse(evt: CustomEvent) {
  const status = evt.detail.xhr.status;
  const toast = document.querySelector("c-toast") as Toast;

  let responseMessage;
  try {
    responseMessage = JSON.parse(evt.detail.serverResponse)["detail"];
  } catch {
    responseMessage = evt.detail.serverResponse;
  }

  if (status >= 200 && status < 300) {
    if (status === 201 && responseMessage.shortened_url) {
      processUrlShortened(responseMessage, toast);
    }
  } else if (status >= 400 && status < 500) {
    toast.show(responseMessage, ToastLevel.WARNING);
  } else if (status >= 500) {
    toast.show("Something went wrong, please try again later.", ToastLevel.ERROR);
  }
}

document.addEventListener("htmx:beforeSwap", toastifyResponse);
