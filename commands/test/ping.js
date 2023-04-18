const { SlashCommandBuilder } = require('discord.js')

module.exports = {
  data: new SlashCommandBuilder().setName('ping').
    setDescription('Replies with Pong!'),
  async execute (interaction) {
    // interaction.reply(`Websocket heartbeat: ${interaction.client.ws.ping}ms.`);
    const sent = await interaction.reply({
      content: 'Pinging...',
      fetchReply: true,
    })
    interaction.editReply(
      `Roundtrip latency: ${
        sent.createdTimestamp - interaction.createdTimestamp
      }ms`,
    )
    interaction.followUp(
      `Websocket heartbeat: ${interaction.client.ws.ping}ms.`)
  },
}
