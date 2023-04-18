// this event is emitted whenever discord-player starts to play a track
module.exports = {
  name: 'playerStart',
  player: true,
  execute (queue, track) {
    // ENTER WHATEVER YOU WANT
    //   queue.metadata.channel.send(`Started playing **${track.title}**!`);
  },
}
