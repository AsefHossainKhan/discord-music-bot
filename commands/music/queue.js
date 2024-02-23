const { SlashCommandBuilder } = require('@discordjs/builders')
const { EmbedBuilder } = require('discord.js')
const { useMainPlayer } = require('discord-player')

module.exports = {
  data: new SlashCommandBuilder().setName('queue').
    setDescription('Shows first 10 songs in the queue'),

  async execute(interaction) {
    const player = useMainPlayer()
    const queue = player.nodes.get(interaction.guildId)

    // check if there are songs in the queue
    if (!queue || !queue.node.isPlaying()) {
      await interaction.reply('There are no songs in the queue')
      return
    }

    // Get the first 10 songs in the queue
    const queueString = queue.tracks.data.slice(0, 10).map((song, i) => {
      return `${i}\. [${song.duration}] ${song.title} - <@${song.requestedBy.id}>`
    }).join('\n')

    // Get the current song
    const currentSong = queue.currentTrack
    await interaction.reply({
      embeds: [
        new EmbedBuilder().setDescription(`**Currently Playing**\n` +
          (currentSong
            ? `\`[${currentSong.duration}]\` ${currentSong.title} - <@${currentSong.requestedBy.id}>`
            : 'None') +
          (queue.tracks.data.length > 0 ? `\n\n**Queue**\n${queueString}` : "\n\n**No more tracks in queue**"),
        ).setThumbnail(currentSong.thumbnail),
      ],
    })
  },
}
