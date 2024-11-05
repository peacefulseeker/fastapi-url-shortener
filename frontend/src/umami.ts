declare global {
  interface Window {
    umami: {
      track: (eventName: string, eventData?: object) => void;
    };
  }
}

if (window.umami === undefined) {
  window.umami = {
    track: function (event, data) {
      console.log(`[DEV] umami track event: ${event}`, data);
    },
  };
}
