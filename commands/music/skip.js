const { SlashCommandBuilder } = require('@discordjs/builders')
const { EmbedBuilder } = require('discord.js')
const { useMasterPlayer } = require('discord-player')

module.exports = {
  data: new SlashCommandBuilder().setName('skip').
    setDescription('Skips the current song'),

  async execute (interaction) {
    const player = useMasterPlayer()

    // Get the queue for the server
    const queue = player.nodes.get(interaction.guildId)

    // If there is no queue, return
    if (!queue) {
      await interaction.reply('There are no songs in the queue')
      return
    }

    const currentSong = queue.currentTrack

    // Skip the current song
    queue.node.skip()

    // Return an embed to the user saying the song has been skipped
    await interaction.reply({
      embeds: [
        new EmbedBuilder().setDescription(
          `${currentSong.title} has been skipped!`).
          setThumbnail(currentSong.thumbnail),
      ],
    })
  },
}
